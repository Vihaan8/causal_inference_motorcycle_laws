"""Build processed/state_year_panel.csv from raw/.

Usage: from the data/ directory, run `python process.py`.
"""

import re
import zipfile
from pathlib import Path

import pandas as pd
import xlrd  # required for .xlw and older .xls files

RAW = Path('raw')
FARS_DIR = RAW / 'fars'
FHWA_DIR = RAW / 'fhwa'
CENSUS   = RAW / 'census'
POLICY   = RAW / 'helmet_law_repeals.csv'
OUT      = Path('processed') / 'state_year_panel.csv'

YEARS = range(1995, 2023)

STATES_50 = {'Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming'}
STATE_SET = STATES_50 | {'District of Columbia'}

FIPS_TO_STATE = {1:'Alabama',2:'Alaska',4:'Arizona',5:'Arkansas',6:'California',8:'Colorado',9:'Connecticut',10:'Delaware',11:'District of Columbia',12:'Florida',13:'Georgia',15:'Hawaii',16:'Idaho',17:'Illinois',18:'Indiana',19:'Iowa',20:'Kansas',21:'Kentucky',22:'Louisiana',23:'Maine',24:'Maryland',25:'Massachusetts',26:'Michigan',27:'Minnesota',28:'Mississippi',29:'Missouri',30:'Montana',31:'Nebraska',32:'Nevada',33:'New Hampshire',34:'New Jersey',35:'New Mexico',36:'New York',37:'North Carolina',38:'North Dakota',39:'Ohio',40:'Oklahoma',41:'Oregon',42:'Pennsylvania',44:'Rhode Island',45:'South Carolina',46:'South Dakota',47:'Tennessee',48:'Texas',49:'Utah',50:'Vermont',51:'Virginia',53:'Washington',54:'West Virginia',55:'Wisconsin',56:'Wyoming'}

EXEMPT_AGE = {'Arkansas':21,'Texas':21,'Kentucky':21,'Florida':21,'Pennsylvania':21,'Michigan':21,'Missouri':26}

# FHWA publication errors: Colorado 2002-2004 and Montana 2007 are ~100x below surrounding years.
REG_SUSPICIOUS = {('Colorado', 2002), ('Colorado', 2003), ('Colorado', 2004), ('Montana', 2007)}

FOOTNOTE = re.compile(r'\s*((?:\(\d+\)|\d+/)(?:\s+(?:\(\d+\)|\d+/))*)\s*$')


def load_fars(year):
    """Return VEHICLE and PERSON tables for a FARS year, handling 4 zip layouts."""
    path = FARS_DIR / f'FARS{year}NationalCSV.zip'
    out = {}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        for t in ('VEHICLE', 'PERSON'):
            matches = [n for n in names if n.lower().split('/')[-1] == f'{t.lower()}.csv']
            with z.open(sorted(matches, key=len)[0]) as f:
                df = pd.read_csv(f, low_memory=False, encoding='latin-1')
            df.columns = df.columns.str.upper()
            out[t] = df
    return out


def motorcycle_fatalities(year):
    d = load_fars(year)
    mc_v = d['VEHICLE'][d['VEHICLE']['BODY_TYP'].between(80, 89)][['ST_CASE', 'VEH_NO']]
    mc_p = d['PERSON'].merge(mc_v, on=['ST_CASE', 'VEH_NO'])
    mc_p = mc_p[(mc_p['INJ_SEV'] == 4) & (mc_p['PER_TYP'].isin([1, 2]))]
    age = pd.to_numeric(mc_p['AGE'], errors='coerce').where(lambda s: s.between(0, 120))
    return (mc_p.assign(_under21=(age < 21), _over21=(age >= 21), _age_known=age.notna())
                 .groupby('STATE').agg(
                     fatalities=('ST_CASE', 'size'),
                     fatalities_under21=('_under21', 'sum'),
                     fatalities_over21=('_over21', 'sum'),
                     fatalities_age_unknown=('_age_known', lambda s: (~s).sum()),
                 ).reset_index()
                 .rename(columns={'STATE': 'state_fips'})
                 .assign(year=year))


def norm_state(s):
    if not isinstance(s, str):
        return None
    s = FOOTNOTE.sub('', s).strip()
    s = re.sub(r'\s+', ' ', s)
    if s in ('Dist. of Col.', 'D.C.'):
        return 'District of Columbia'
    return s if s in STATE_SET else None


def read_mv1_sheet(path):
    if path.suffix == '.xlw':
        sh = xlrd.open_workbook(str(path)).sheet_by_index(0)
        return pd.DataFrame([[sh.cell(r, c).value for c in range(sh.ncols)] for r in range(sh.nrows)])
    return pd.read_excel(path, header=None)


def parse_mv1(path):
    df = read_mv1_sheet(path)
    # MOTORCYCLES header is the rightmost group pre-2011, a middle group post-2011.
    # Find the first cell containing MOTORCYCLE; take that column and the two to its right.
    mc = next(((r, c) for r in range(min(15, len(df))) for c in df.columns
               if isinstance(df.iat[r, c], str) and 'MOTORCYCLE' in df.iat[r, c].upper()), None)
    if not mc:
        raise ValueError(f'MOTORCYCLES header not found in {path}')
    slot = [mc[1] + i for i in range(3) if (mc[1] + i) in df.columns]
    rows = []
    for _, row in df.iterrows():
        name = norm_state(str(row[0])) if pd.notna(row[0]) else None
        if not name:
            continue
        nums = pd.to_numeric(row[slot], errors='coerce').dropna()
        if len(nums):
            rows.append({'state': name, 'motorcycles': int(nums.max())})
    return pd.DataFrame(rows).drop_duplicates(subset='state', keep='last')


def load_fars_panel():
    parts = [motorcycle_fatalities(y) for y in YEARS]
    fars = pd.concat(parts, ignore_index=True)
    fars['state'] = fars['state_fips'].map(FIPS_TO_STATE)
    return fars.drop(columns=['state_fips']).dropna(subset=['state'])


def load_mv1_panel():
    parts = []
    for f in sorted(FHWA_DIR.glob('mv1_*.*')):
        year = int(f.stem.split('_')[1])
        parts.append(parse_mv1(f).assign(year=year))
    return pd.concat(parts, ignore_index=True)


def load_population_panel():
    # 1995-1999 from ST-99-3 txt. File has two blocks: block 1 (1994-1999), block 2 (1990-1993).
    # Restrict to block 1.
    rows = []
    with open(CENSUS / 'pop_1990_2000.txt') as fh:
        for line in fh:
            m = re.match(r'\s+1\s+(.+?)\s{2,}([\d\s]+)$', line.rstrip())
            if not m:
                continue
            name = m.group(1).strip()
            if name not in STATE_SET:
                continue
            nums = [int(x) for x in m.group(2).split()]
            for yr, val in zip([1999, 1998, 1997, 1996, 1995], nums[:5]):
                rows.append({'state': name, 'year': yr, 'population': val})
    parts = [pd.DataFrame(rows)]

    d = pd.read_csv(CENSUS / 'pop_2000_2010.csv')
    d = d[(d.SEX == 0) & (d.ORIGIN == 0) & (d.RACE == 0) & (d.AGEGRP == 0) & d.NAME.isin(STATE_SET)]
    parts += [d[['NAME']].assign(year=y, population=d[f'POPESTIMATE{y}'].astype(int))
                         .rename(columns={'NAME': 'state'}) for y in range(2000, 2010)]

    for fname, yrs in [('pop_2010_2020.csv', range(2010, 2020)),
                       ('pop_2020_2024.csv', range(2020, 2023))]:
        d = pd.read_csv(CENSUS / fname)
        d = d[d.NAME.isin(STATE_SET)]
        parts += [d[['NAME']].assign(year=y, population=d[f'POPESTIMATE{y}'].astype(int))
                             .rename(columns={'NAME': 'state'}) for y in yrs]

    return pd.concat(parts, ignore_index=True)


def build_panel():
    fars = load_fars_panel()
    reg  = load_mv1_panel()
    pop  = load_population_panel()
    pol  = pd.read_csv(POLICY)
    pol['exemption_age'] = pol['state'].map(EXEMPT_AGE)

    panel = (fars.merge(reg, on=['state', 'year'])
                 .merge(pop, on=['state', 'year'])
                 .merge(pol, on='state', how='left'))

    panel['treated']    = panel['repeal_year'].notna().astype(int)
    panel['post']       = (panel['year'] >= panel['repeal_year']).fillna(False).astype(int)
    panel['event_time'] = panel['year'] - panel['repeal_year']
    panel['fatality_rate_per_10k_reg']  = panel['fatalities'] / (panel['motorcycles'] / 10_000)
    panel['fatality_rate_per_100k_pop'] = panel['fatalities'] / (panel['population'] / 100_000)

    panel['reg_data_quality_flag'] = panel.apply(
        lambda r: 'suspicious_low' if (r['state'], r['year']) in REG_SUSPICIOUS else 'ok',
        axis=1,
    )

    cols = ['state', 'year',
            'fatalities', 'fatalities_under21', 'fatalities_over21', 'fatalities_age_unknown',
            'motorcycles', 'fatality_rate_per_10k_reg',
            'population', 'fatality_rate_per_100k_pop',
            'treated', 'repeal_year', 'event_time', 'post', 'exemption_age',
            'reg_data_quality_flag']
    panel = panel[cols].sort_values(['state', 'year']).reset_index(drop=True)
    panel['repeal_year']   = panel['repeal_year'].astype('Int64')
    panel['event_time']    = panel['event_time'].astype('Int64')
    panel['exemption_age'] = panel['exemption_age'].astype('Int64')
    return panel


def main():
    panel = build_panel()
    OUT.parent.mkdir(exist_ok=True)
    panel.to_csv(OUT, index=False)

    treated = sorted(panel.loc[panel.treated == 1, 'state'].unique())
    flagged = panel.loc[panel.reg_data_quality_flag == 'suspicious_low', ['state', 'year']].values.tolist()

    print(f'wrote {OUT}')
    print(f'  rows: {len(panel)}  cols: {len(panel.columns)}')
    print(f'  years: {panel.year.min()}-{panel.year.max()}  states: {panel.state.nunique()}')
    print(f'  treated states ({len(treated)}): {", ".join(treated)}')
    print(f'  flagged state-years (kept, reg_data_quality_flag=suspicious_low):')
    for s, y in flagged:
        print(f'    {s} {y}')


if __name__ == '__main__':
    main()
