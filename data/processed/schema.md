# state_year_panel.csv — schema

One row per state-year. 51 states (50 + DC) x 28 years (1995-2022) = 1,428 rows.

| Column | Type | Source | Description |
|---|---|---|---|
| `state` | str | FARS + FHWA | Full state name (e.g., `Pennsylvania`, `District of Columbia`). Key. |
| `year` | int | FARS + FHWA | Calendar year, 1995-2022. Key. |
| `fatalities` | int | FARS | Motorcycle-occupant fatalities. Filter: `BODY_TYP` in 80-89, `INJ_SEV == 4`, `PER_TYP` in {1, 2}. Matches NHTSA published annual totals to within ~5. |
| `fatalities_under21` | int | FARS | Subset of `fatalities` where age < 21. Used for the age-heterogeneity placebo check. |
| `fatalities_over21` | int | FARS | Subset where age >= 21. |
| `fatalities_age_unknown` | int | FARS | Fatalities where AGE is missing/sentinel. `fatalities` = `_under21 + _over21 + _age_unknown`. |
| `motorcycles` | int | FHWA MV-1 | Registered motorcycles in the state-year. Taken from the MOTORCYCLES column group (private + commercial + publicly owned), max of the three. |
| `fatality_rate_per_10k_reg` | float | computed | `fatalities / (motorcycles / 10_000)`. Primary outcome. |
| `treated` | 0/1 | policy | 1 if the state ever repealed its universal helmet law in our window. |
| `repeal_year` | int or NaN | policy | The calendar year the state's repeal took effect. NaN for controls. |
| `event_time` | int or NaN | computed | `year - repeal_year`. Negative = pre-repeal, 0 = year of repeal, positive = post. NaN for controls. |
| `post` | 0/1 | computed | 1 if `year >= repeal_year`, else 0. 0 for all control-state rows. |
| `exemption_age` | int or NaN | policy | Minimum age at which the repeal exempts riders from wearing a helmet. 21 for 6 of 7 treated states; 26 for Missouri. NaN for controls. |
| `reg_data_quality_flag` | str | manual | `'ok'` or `'suspicious_low'`. The latter marks four state-years where FHWA's published registrations are ~100x below surrounding years: Colorado 2002, 2003, 2004 and Montana 2007. Retained in the panel; analyses should consider excluding. |
| `population` | int | Census NST-EST | State resident population estimate, July 1 of the year. Sourced from four Census release eras (1990-2000 txt, 2000-2010 intercensal, 2010-2020 vintage, 2020-2024 vintage) stitched into one panel. |
| `fatality_rate_per_100k_pop` | float | computed | `fatalities / (population / 100_000)`. Robustness outcome. |

## Notes

- `fatalities` aligns with NHTSA's published headline "motorcycle fatalities" because it includes all BODY_TYP 80-89 (moped, 3-wheel, off-road, etc.), not only 80 (street motorcycle). 95% of the count is code 80.
- FARS helmet-use coding has three eras across 1995-2022 (REST_USE old codes, REST_USE new codes, HELM_USE). This panel does not include a helmet-use column; if Figure 4 in the proposal is produced, a separate harmonization step is required.
- Age threshold is hard-coded to 21 for the under/over split, per proposal. Missouri's exemption age is 26, so its under-21 subset does not correspond to "exempt" vs "required"; interpret `fatalities_under21` for Missouri with that caveat. The `exemption_age` column is the right variable if you need the state-specific split.
- Treated states: Arkansas (1997), Texas (1997), Kentucky (1998), Florida (2000), Pennsylvania (2003), Michigan (2012), Missouri (2020). All are partial repeals (adults exempted).
