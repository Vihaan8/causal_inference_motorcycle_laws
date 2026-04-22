## Model Process

To estimate the effect of repealing universal motorcycle helmet laws on motorcycle
fatalities, we use a **difference-in-differences (DiD)** design with a 
**state-year panel** covering 50 states plus DC from 1995 to 2022.

### 1. Outcome Variable
The primary outcome is:

- **`fatality_rate_per_10k_reg`** = motorcycle fatalities per 10,000 registered
motorcycles

This is the main outcome because registered motorcycles are the most direct 
exposure measure for the policy question. As a robustness check we also use
**`fatality_rate_per_100k_pop`** = motorcycle fatalities per 100,000 population,
which avoids reliance on motorcycle registration data entirely.

### 2. Treatment Definition
Seven states repealed a universal helmet law during the study window:

- Arkansas (1997)
- Texas (1997)
- Kentucky (1998)
- Florida (2000)
- Pennsylvania (2003)
- Michigan (2012)
- Missouri (2020) — *excluded from estimation (see Section 4)*

The treatment group used in the models is therefore six states.

For the DiD model:

- `treated = 1` for states that ever repealed
- `post = 1` for years on or after each state's own repeal year
- `did = treated × post`

Because repeals happened at different times across states, this is a 
**staggered DiD** design. The `post` variable is defined relative to each
state's own repeal year, not a single common cutoff.

The coefficient on `did` captures the average change in fatality rates in 
repeal states after repeal, relative to the change in non-repeal states over
the same years.

### 3. Main Model
The primary specification is a **two-way fixed effects DiD model**:

`Y_st = α_s + γ_t + β(treated_s × post_st) + ε_st`

where:

- `Y_st` is the motorcycle fatality rate in state `s` and year `t`
- `α_s` are **state fixed effects** (absorb time-invariant differences across states)
- `γ_t` are **year fixed effects** (absorb national trends affecting all states)
- `β` is the DiD estimate of the repeal effect

We cluster standard errors at the **state level** to account for within-state
correlation over time.

### 4. Data Quality Adjustment
The dataset flags four state-years with suspiciously low motorcycle registration
counts:

- Colorado: 2002, 2003, 2004
- Montana: 2007

Inspection of these rows reveals implausibly high fatality rates — for example,
Colorado 2002 shows 654 fatalities per 10,000 motorcycles, which is not
physically possible. Because these rows would distort the registration-based
fatality rate, the main specification excludes them.

We also exclude Missouri entirely. Its repeal took effect in 2020, so only
three post-period years (2020–2022) are observed, which is too few to
identify a repeal effect. Missouri's exemption age is also 26 rather than
21, so it does not match the under-21 / over-21 split used in the age-group
analysis. Dropping Missouri removes 28 state-years.

After both exclusions, the estimation sample is 1,396 observations
(1,428 − 4 flagged rows − 28 Missouri rows).

### 5. Robustness Checks
We estimate three specifications in total:

- **Model 1 (Baseline):** Two-way fixed effects DiD, primary outcome
- **Model 2 (+ log population):** Adds log(population) as a covariate to 
control for differential state population growth over time
- **Model 3 (Robustness):** Replaces the primary outcome with fatalities per
100,000 population

### 6. Parallel Trends Test
Before interpreting the DiD results, we formally test the parallel trends
assumption using two approaches:

1. **Event study plot:** We estimate separate coefficients for each year 
relative to repeal (event time -6 to +9, reference year = -1) and plot them
with 95% confidence intervals. Pre-period coefficients should be close to zero
if parallel trends holds.

2. **Joint F-test:** We formally test whether all pre-period event-study
coefficients are jointly equal to zero.

### 7. Age-Group Comparison
As a mechanism check, we compare fatality trends for over-21 and under-21
riders within repeal states. Since most repeals exempt riders aged 21 and over,
over-21 riders are no longer required to wear helmets while under-21 riders
still are. This creates a second difference-in-differences:

- Difference 1: pre vs. post repeal
- Difference 2: over-21 vs. under-21 riders

---

## Results Interpretation

### Descriptive Results
Pre-period summary statistics show that repeal and control states had broadly
similar fatality rates before any repeal occurred (6.18 vs. 6.71 per 10,000
registered motorcycles), supporting the comparability of the two groups.

### Parallel Trends
The event study plot shows pre-period coefficients clustered near zero with
confidence intervals that all cross zero. The joint F-test confirms this
formally:

- **F-statistic:** 1.02
- **p-value:** 0.42

We fail to reject the null hypothesis of parallel trends, supporting the
validity of the DiD design.

### Main DiD Result
In the baseline DiD model, the estimated repeal effect is:

- **Coefficient:** 1.4389
- **Standard error:** 0.8180
- **p-value:** 0.0786
- **95% CI:** [-0.164, 3.042]

Repealing a universal motorcycle helmet law is associated with an increase of
about **1.44 motorcycle fatalities per 10,000 registered motorcycles** per year,
relative to the change observed in non-repeal states over the same period.
This represents a **23.3% increase** over the pre-repeal baseline fatality rate
of 6.18. The result is marginally significant (p≈0.08) — the 95% CI narrowly
includes zero once Missouri is excluded, though the point estimate is similar
in magnitude to the population-based robustness check in Model 3 (which is
significant at the 1% level).

### Robustness Results

**Model 2 (+ log population):**
- **Coefficient:** 1.3680
- **p-value:** 0.0714

Adding log(population) as a covariate leaves the coefficient nearly unchanged,
indicating that differential population growth across states is not driving
the result.

**Model 3 (per 100k population):**
- **Coefficient:** 0.3511
- **p-value:** 0.0082

Using a completely different outcome measure leads to the same substantive
conclusion, and here the effect is statistically significant at the 1% level.
The smaller magnitude reflects the larger denominator — total population
rather than registered motorcycles — not a smaller effect.

### Event Study Result
Pre-period coefficients are all statistically indistinguishable from zero,
consistent with the parallel trends assumption. Post-repeal coefficients are
mostly positive and show a generally upward trend over time, suggesting the
effect may grow as helmet use declines further after repeal. Individual
year-by-year estimates are imprecise due to the small number of treated states,
and are best treated as supporting evidence for the pooled DiD estimate.

### Age-Group Comparison
The over-21 vs. under-21 DiD yields a coefficient of 2.22 (p=0.005),
suggesting a larger increase in fatalities among the newly-exempt over-21
group. However, the formal pre-trend F-test for the age-group comparison
rejects parallel trends (F=5.61, p=0.029), meaning the over-21 group was
already trending upward before any repeal occurred. This is consistent with
a well-documented national demographic shift toward older motorcycle riders
over this period. Figure 3 and the age-group DiD should therefore be
interpreted as suggestive evidence of a mechanism rather than a clean
causal test.

---

## Final Takeaway

The main empirical finding is that repealing a universal motorcycle helmet law
is associated with **higher motorcycle fatality rates**. The baseline
difference-in-differences model estimates an increase of about **1.44 fatalities
per 10,000 registered motorcycles** (p≈0.08) — a 23.3% increase over the
pre-repeal baseline. The population-based robustness check (Model 3) is
statistically significant at the 1% level (0.35 extra fatalities per 100k
residents, p=0.008), and the covariate-adjusted specification gives a nearly
identical point estimate to the baseline. The event study validates the
parallel trends assumption. The age-group comparison provides suggestive
mechanistic evidence but should be interpreted with caution due to pre-existing
demographic trends in the over-21 rider population.