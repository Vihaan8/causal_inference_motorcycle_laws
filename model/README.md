## Model Process

To estimate the effect of repealing universal motorcycle helmet laws on motorcycle fatalities, we use a **difference-in-differences (DiD)** design with a **state-year panel** covering 50 states plus DC from 1995 to 2022.

### 1. Outcome variable
The primary outcome is:

- **`fatality_rate_per_10k_reg`** = motorcycle fatalities per 10,000 registered motorcycles

This is the main outcome because registered motorcycles are the most direct exposure measure for the policy question.

### 2. Treatment definition
The treatment group includes the seven states that repealed a universal helmet law during the study window:

- Arkansas
- Texas
- Kentucky
- Florida
- Pennsylvania
- Michigan
- Missouri

For the DiD model:

- `treated = 1` for states that ever repealed
- `post = 1` for years after the repeal took effect
- `did = treated × post`

The coefficient on `did` captures the average change in fatality rates in repeal states after repeal, relative to the change in non-repeal states over the same years.

### 3. Main model
The primary specification is a **two-way fixed effects DiD model**:


`Y_st = α_s + γ_t + β(treated_s × post_st) + ε_st`

where:

- `Y_st` is the motorcycle fatality rate in state `s` and year `t`
- `α_s` are **state fixed effects**
- `γ_t` are **year fixed effects**
- `β` is the DiD estimate of the repeal effect

We cluster standard errors at the **state level** to account for within-state correlation over time.


### 4. Data quality adjustment
The dataset flags four state-years with suspiciously low motorcycle registration counts:

- Colorado: 2002, 2003, 2004
- Montana: 2007

Because these rows could distort the registration-based fatality rate, the main specification excludes them. This clean-sample model is used as the headline result.

### 5. Robustness check
To confirm the finding is not driven only by the motorcycle registration denominator, we estimate a second DiD model using:

- **`fatality_rate_per_100k_pop`** = motorcycle fatalities per 100,000 population

This provides a robustness check using population as an alternative denominator.

### 6. Event-study model
We also estimate an event-study specification centered on repeal year. This model is used to check whether treated and control states followed similar trends before repeal and to examine how the estimated effect evolves over time.

The year before repeal is the omitted reference period, so each event-time coefficient is interpreted relative to that year.

---

## Results Interpretation

### Main DiD result
In the clean-sample DiD model, the estimated repeal effect is:

- **Coefficient:** 1.6129
- **Standard error:** 0.7647
- **p-value:** 0.0349

### Interpretation
This means that, on average, repealing a universal motorcycle helmet law is associated with an increase of about **1.61 motorcycle fatalities per 10,000 registered motorcycles**, relative to the change observed in non-repeal states over the same period.

Because the p-value is below 0.05, this result is statistically significant at conventional levels.

### Robustness result
In the population-based robustness model where we drop the state-years flagged for suspiciously low motorcycle registration counts, the estimated repeal effect is:

- **Coefficient:** 0.3777
- **Standard error:** 0.1262
- **p-value:** 0.0028

### Interpretation
Using fatalities per 100,000 population leads to the same substantive conclusion: repeal is associated with a higher motorcycle fatality rate. This strengthens confidence that the result is not driven only by measurement issues in motorcycle registration counts.

### Event-study result
The event-study coefficients before repeal are all statistically indistinguishable from zero, which is consistent with the parallel-trends assumption. After repeal, most coefficients are positive, suggesting higher fatality rates following repeal. However, the year-by-year estimates are imprecise and not individually statistically significant.

### Interpretation
The event study supports the DiD design because it does not show strong evidence of differential trends before repeal. At the same time, the post-repeal pattern is generally positive, which is directionally consistent with the main DiD estimate. Since the event-study coefficients are estimated year by year, they are noisier than the pooled main DiD estimate and are best treated as supporting evidence rather than the headline result.

---

## Final Takeaway

The main empirical finding is that repealing a universal motorcycle helmet law is associated with **higher motorcycle fatality rates**. The clean-sample difference-in-differences model suggests an increase of about **1.61 fatalities per 10,000 registered motorcycles**, and this conclusion is supported by a population-based robustness check. Overall, the evidence is consistent with the view that helmet law repeal increases motorcycle fatality risk.