# Motorcycle helmet law repeals and fatality rates

Causal question: does repealing a universal motorcycle helmet law increase motorcycle fatalities? We answer it with a difference-in-differences design over seven states that repealed their universal laws between 1997 and 2020 (Arkansas, Texas, Kentucky, Florida, Pennsylvania, Michigan, Missouri) against the rest of the country, 1995-2022. Missouri is in the panel but excluded from estimation (2020 repeal leaves too few post-period years; see `models/README.md` §4), so the DiD models are fit on six treated states vs. 44 controls.

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

## Reproduce

```
cd data
python process.py
```

Reads `data/raw/`, writes `data/processed/state_year_panel.csv`. No network calls, no manual steps.

## More

- **Data dictionary** (every column in the processed panel, with type, source, and definition): [data/processed/schema.md](data/processed/schema.md)
- **Raw-data inventory** (what's in `raw/` by folder, source URLs, format quirks): [data/README.md](data/README.md)
- **EDA notebook** (how the cleaning decisions were reached, with validation against NHTSA's published totals): [data/eda.ipynb](data/eda.ipynb)
