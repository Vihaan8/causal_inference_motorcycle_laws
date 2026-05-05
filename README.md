# Motorcycle helmet law repeals and fatality rates

Causal question: does repealing a universal motorcycle helmet law increase motorcycle fatalities? We answer it with a staggered difference-in-differences design over seven states that repealed their universal laws between 1997 and 2020 (Arkansas, Texas, Kentucky, Florida, Pennsylvania, Michigan, Missouri) against the rest of the country, 1995-2022. Missouri is in the panel but excluded from estimation (2020 repeal leaves too few post-period years; see `models/README.md` §4), so the DiD models are fit on six treated states vs. 44 controls.

## Contents

- [Background](#background)
- [Data collection](#data-collection)
- [How the panel supports the causal question](#how-the-panel-supports-the-causal-question)
- [Methods](#methods)
- [Findings](#findings)
- [Caveats](#caveats)
- [Repository layout](#repository-layout)
- [Reproduce](#reproduce)
- [More](#more)

## Background

Motorcycle crashes kill roughly 6,000 riders each year in the US, and NHTSA estimates that helmets prevent about 37% of those deaths. Nineteen states plus DC currently require all riders to wear helmets; 28 states require them only for minors; 3 states have no helmet law. Seven states moved from universal to partial coverage between 1997 and 2020, and more legislatures consider similar bills every session. Prior evaluations have either compared partial-law states to universal-law states cross-sectionally (which mixes the law's effect with stable state-level differences) or looked at single-state pre/post changes (which mixes the law with national trends). DiD resolves both confounders at once.

## Data collection

Four independent sources are needed because no single dataset contains both the numerator (motorcycle deaths) and the denominator (how many motorcycles or people are at risk) together with the treatment timing. The pipeline joins them into one state-year panel.

```mermaid
flowchart LR
    A["<b>FARS</b><br/>US federal record of every<br/>fatal road crash since 1975<br/><i>provides: motorcycle deaths<br/>per state per year</i>"]:::raw --> M["merge on<br/>state + year"]
    B["<b>FHWA MV-1</b><br/>Federal Highway Administration<br/>annual state motorcycle<br/>registration counts<br/><i>provides: primary denominator<br/>(exposure — bikes at risk)</i>"]:::raw --> M
    C["<b>Census NST-EST</b><br/>US Census Bureau annual<br/>state population estimates<br/><i>provides: secondary denominator<br/>(robustness — deaths per capita)</i>"]:::raw --> M
    D["<b>Policy table</b><br/>Hand-coded from GHSA / IIHS<br/>which states repealed their<br/>universal helmet law and when<br/><i>provides: treatment indicator</i>"]:::raw --> M
    M --> O["<b>state_year_panel.csv</b><br/>one row per state per year<br/>with fatality rates and<br/>treatment variables"]:::out
    classDef raw fill:#eef,stroke:#557
    classDef out fill:#efe,stroke:#575
```

## How the panel supports the causal question

Difference-in-differences asks: *did fatality rates in repeal states change more after the repeal than fatality rates in non-repeal states over the same years?* If yes, the extra change is the causal effect of the repeal. The panel is structured so this comparison is a direct computation.

```mermaid
flowchart LR
    panel["<b>state-year panel</b><br/>50 states + DC<br/>x 28 years<br/>(1995-2022)"]:::p --> treat["<b>6 treated states</b><br/>repealed universal<br/>helmet laws, 1997-2012<br/><i>(Missouri 2020 dropped —<br/>too few post years)</i>"]:::t
    panel --> ctrl["<b>44 control states</b><br/>kept universal helmet<br/>laws unchanged"]:::c
    treat --> did{"<b>diff-in-diff<br/>+ event study</b><br/>compare fatality rate<br/>change across groups<br/>before vs. after repeal"}
    ctrl --> did
    did --> effect["<b>causal estimate</b><br/>of how repeal affects<br/>motorcycle fatality rate"]:::e
    classDef p fill:#efe,stroke:#575
    classDef t fill:#fee,stroke:#755
    classDef c fill:#eef,stroke:#557
    classDef e fill:#ffe,stroke:#775
```

## Methods

The estimation sample is 1,396 state-years: the 1,428 raw rows minus 28 Missouri rows and 4 FHWA registration outliers (Colorado 2002–2004 and Montana 2007, all ~100× below their surrounding years). Four specifications are estimated:

| Model | Outcome | Notes |
|---|---|---|
| 1. Baseline TWFE DiD | fatalities / 10k registered motorcycles | state + year fixed effects, SEs clustered by state |
| 2. + Population control | same | adds log(population) as a covariate |
| 3. Population-based | fatalities / 100k residents | swaps the denominator to address registration-data noise |
| 4. Triple-difference | over-21 minus under-21 fatality gap | tests whether the effect concentrates in the exempt age group |

Parallel trends are tested with an event study: separate coefficients for each event-time relative to repeal (binned into two-year groups for precision), with a joint F-test on the pre-period. Both the pooled DiD and the triple-difference pass.

## Findings

Partial repeal raises motorcycle fatalities by about 23%. Baseline DiD: **+1.44 deaths per 10,000 registered motorcycles** per year (p≈0.08, against a 6.18 pre-repeal baseline). Robustness specifications agree — adding log(population) barely moves the estimate (1.37), and switching the denominator to state residents (cleaner, since registration counts are noisy) gives **+0.35 per 100,000 residents** (p<0.01).

Pre-repeal trends are statistically indistinguishable across the two groups (binned event study F=0.74, p=0.53), so the post-repeal divergence is not the continuation of a pre-existing gap. The increase concentrates in the over-21 riders that partial repeals exempt: a triple-difference against under-21 riders yields **+1.59 per 10,000** (p<0.001) with clean pre-trends (F=0.39, p=0.86). The effect also grows over time — 0.91 in years 0–3, 1.52 in year 4+ — consistent with helmet-wearing habits decaying gradually after the universal requirement is removed.

## Caveats

- **Six treated states is a small cluster count.** Standard errors clustered at the state level are conservative; the baseline registration-based estimate sits just outside conventional significance (p≈0.08), while the population-based specification (cleaner denominator, less measurement error) clears p<0.01 and is the more defensible anchor.
- **FHWA registration data is noisy.** Four state-years are dropped outright due to publication errors (Colorado 2002–2004 and Montana 2007). Model 3's switch to a population denominator is partly designed around this concern.
- **Missouri (2020) is excluded.** Only three post-period years are observed and its exemption age is 26 rather than 21, so it does not match the under-21 / over-21 split used in the triple-difference.
- **No rider-level demographics.** FARS does not have race, income, or insurance status at the granularity needed to test whether the fatality increase falls disproportionately on any group.

## Repository layout

```
.
├── data/
│   ├── process.py           # builds the panel from raw/
│   ├── eda.ipynb            # cleaning decisions, NHTSA-total validation
│   ├── README.md            # raw-data inventory
│   ├── raw/                 # FARS, FHWA MV-1, Census, helmet_law_repeals.csv
│   └── processed/
│       ├── state_year_panel.csv
│       └── schema.md        # column dictionary
├── models/
│   ├── did.ipynb            # DiD, event study, triple-diff, time-split
│   └── README.md            # methodology and results writeup
├── Figures/                 # binned event study, triple-diff age gap, treated-state trajectories
└── IDS 701 Final Report_submission.pdf
```

The raw data files (FARS zips, FHWA xls/xlsx, Census csvs) are not committed — only the hand-coded `helmet_law_repeals.csv` is. See `data/README.md` for source URLs.

## Reproduce

```
cd data
python process.py
```

Reads `data/raw/`, writes `data/processed/state_year_panel.csv`. No network calls, no manual steps.

## More

- **Final report** (the writeup these findings appear in): [IDS 701 Final Report_submission.pdf](IDS%20701%20Final%20Report_submission.pdf)
- **Modeling notebook and writeup** (every specification, parallel-trends test, and event study): [models/did.ipynb](models/did.ipynb), [models/README.md](models/README.md)
- **Data dictionary** (every column in the processed panel, with type, source, and definition): [data/processed/schema.md](data/processed/schema.md)
- **Raw-data inventory** (what's in `raw/` by folder, source URLs, format quirks): [data/README.md](data/README.md)
- **EDA notebook** (how the cleaning decisions were reached, with validation against NHTSA's published totals): [data/eda.ipynb](data/eda.ipynb)
