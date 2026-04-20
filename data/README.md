# Data

## raw/

### fars/
FARS yearly national ZIPs, 1995-2022, one file per year (`FARS{year}NationalCSV.zip`).
Source: https://www.nhtsa.gov/research-data/fatality-analysis-reporting-system-fars
Each ZIP contains ACCIDENT, VEHICLE, and PERSON tables (plus supplemental tables in later years).
Layout note: pre-2010ish ZIPs have flat uppercase CSVs at the root; 2010+ nest lowercase CSVs under `FARS{year}NationalCSV/` with paired `*NAME` decoded columns and a UTF-8 BOM.

### fhwa/
FHWA Highway Statistics Table MV-1, State Motor-Vehicle Registrations, 1995-2022, one file per year (`mv1_{year}.{ext}`).
Source: https://www.fhwa.dot.gov/policyinformation/statistics.cfm
Formats vary by year: `.xlw` (1996, Excel 4.0), `.xls` (1995, 1997-2014), `.xlsx` (2015-2022).
Each file has a multi-row header; state rows start around row 9-12; motorcycle counts appear in the MOTORCYCLES column group (private / publicly owned / total).

### helmet_law_repeals.csv
Policy treatment table. Columns: `state`, `repeal_year`. Seven treated states: Arkansas (1997), Texas (1997), Kentucky (1998), Florida (2000), Pennsylvania (2003), Michigan (2012), Missouri (2020).
Source: GHSA, cross-checked with IIHS (https://www.iihs.org/topics/motorcycles). Written by hand, no download.

### census/
US Census state population estimates, 1995-2022. Four files spanning different release eras: `pop_1990_2000.txt`, `pop_2000_2010.csv`, `pop_2010_2020.csv`, `pop_2020_2024.csv`. Used to build the `population` column and the `fatalities_per_100k_pop` robustness outcome.
Source: https://www2.census.gov/programs-surveys/popest/

## processed/

### state_year_panel.csv
One row per state-year, 1,428 rows (51 states x 28 years). Built from the raw sources by `process.py`. Column dictionary in `schema.md`.

### schema.md
Column dictionary for `state_year_panel.csv`.

## Running the pipeline

```
python process.py
```

Run from this directory. Reads `raw/`, writes `processed/state_year_panel.csv`, prints a short summary (row count, year range, treated states, and any data-quality flags).
