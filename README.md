# Motorcycle helmet law repeals and fatality rates

Causal question: does repealing a universal motorcycle helmet law increase motorcycle fatalities? We answer it with a difference-in-differences design over seven treated states (Arkansas 1997, Texas 1997, Kentucky 1998, Florida 2000, Pennsylvania 2003, Michigan 2012, Missouri 2020) against the rest of the country, 1995-2022.

## Data collection

```mermaid
flowchart LR
    A[NHTSA FARS<br/>28 yearly zips]:::raw --> P[process.py]
    B[FHWA MV-1<br/>28 Excel files]:::raw --> P
    C[Census NST-EST<br/>4 decade files]:::raw --> P
    D[helmet_law_repeals.csv<br/>7 treated states]:::raw --> P
    P --> O[processed/<br/>state_year_panel.csv<br/>1,428 rows x 16 cols]:::out
    classDef raw fill:#eef,stroke:#557
    classDef out fill:#efe,stroke:#575
```

FARS gives motorcycle-occupant fatalities. FHWA MV-1 gives registered motorcycles per state-year (primary denominator). Census NST-EST gives state population (robustness denominator). The policy CSV encodes the treatment dates. `process.py` joins them into one state-year panel.

## How the panel supports the causal question

```mermaid
flowchart LR
    panel[state_year_panel.csv<br/>51 states x 28 years]:::p --> treat[7 treated states<br/>repeal 1997-2020]:::t
    panel --> ctrl[44 control states]:::c
    treat --> did{Diff-in-diff<br/>+ event study}
    ctrl --> did
    did --> effect[Effect on<br/>fatality rate per 10k<br/>registered motorcycles]:::e
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

Reads everything from `data/raw/`, writes `data/processed/state_year_panel.csv`. No network calls, no manual steps.

## More

Data-layer details (sources, formats, column schema, known issues): see [data/README.md](data/README.md).
