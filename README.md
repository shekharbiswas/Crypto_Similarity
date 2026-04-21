## Crypto Similarity Framework

### Goal
Identify redundant crypto assets to avoid unnecessary fund transfers.

### Universe
~500 coins in → ~150–200 working universe → pairwise similarity scores

--------------------------------------------------

5 PHASES

--------------------------------------------------
### PHASE 1 — DATA PREP & VALIDITY
--------------------------------------------------

Filter the universe and confirm math is valid before touching any statistics.

Coverage filter
Minimum 400 trading days

Stablecoin removal
Remove stablecoins including algorithmic ones even if is_stablecoin = False

Amihud Illiquidity Filter
Drop top 20% most illiquid assets
Hard floor rule: median volume < $500K removed

Stationarity Tests on Log Returns
ADF test
KPSS test

If ADF and KPSS conflict:
Estimate ARFIMA fractional differencing parameter

Multiple Testing Control
Benjamini–Hochberg False Discovery Rate correction
Applied to every p-value downstream

Outputs

data/
  universe_filtered.csv
  coin_metadata.csv

coin_metadata.csv fields
  amihud_illiquidity
  arfima_nu
  fractional_differencing_d

--------------------------------------------------
### PHASE 2 — SIMILARITY SIGNALS
--------------------------------------------------

Build the core pairwise signal matrix.

Core Data
Log returns matrix (T × N)

Correlation Signals
Pearson correlation
Spearman correlation

Rolling correlations
  30 day window
  90 day window

Market Factor Adjustment
BTC-beta adjusted correlation
Partial out BTC market factor

Tail Dependence via Copulas

For every asset pair fit three copula families:

Clayton
Gumbel
Joe–Clayton

Extract:

λL (lower tail dependence)
Crash similarity

λU (upper tail dependence)
Rally similarity

Outputs

signals/
  correlation_matrices.parquet
  tail_dependence_lower.parquet
  tail_dependence_upper.parquet

--------------------------------------------------
### PHASE 3 — REGIME & STRUCTURE
--------------------------------------------------

Confirm similarity holds across regimes and long-run relationships.

Market Regime Detection

Fit 2-state Markov Regime Switching model on BTC returns.

Regimes

Bull
Bear

Compute pairwise correlation within each regime

ρ_bull
ρ_bear

Cointegration Testing

Apply Engle–Granger cointegration test
Only run on pairs where correlation > 0.6

Adjust p-values using BH-FDR correction.

TVECM (Threshold Vector Error Correction Model)

For cointegrated pairs extract

Neutral band width
Mean reversion speed

Leadership Detection

Within clusters run Granger causality tests
Identify the leader coin for each cluster

Outputs

structure/
  regime_labels.csv
  regime_corr.parquet
  cointegration_results.csv
  granger_causality.csv

--------------------------------------------------
### PHASE 4 — COMPOSITE SCORE & CLUSTERING
--------------------------------------------------

Combine all signals into one similarity score.

Score Components and Weights

Rolling correlation (90d)              20%
BTC-adjusted correlation               10%
Lower tail dependence λL               25%
Bear-regime correlation                20%
Cointegration (binary + speed)         15%
GLASSO partial correlation             10%

Normalization

All components are min-max normalized before aggregation.

Similarity Score

similarity_score = weighted_sum(normalized_components)

Clustering

Distance metric
1 − similarity_score

Clustering algorithm
Hierarchical clustering

Linkage method
Ward linkage

Optimal cluster count

Search range
k = 5 to 30

Select k using silhouette score.

Representative Coin per Cluster

Choose the coin that satisfies:

Highest trading volume
Lowest Amihud illiquidity
Granger leader within cluster

Outputs

results/
  composite_similarity.parquet
  cluster_assignments.csv
  transfer_rules.csv

--------------------------------------------------
TRANSFER CLASSIFICATION
--------------------------------------------------

Score Range        Classification            Action

0.80 – 1.00        Highly Redundant          Avoid transfer
0.60 – 0.79        Moderately Redundant      Marginal benefit only
0.40 – 0.59        Partially Similar         Sector overlap
0.00 – 0.39        Distinct                  Transfer adds diversification

--------------------------------------------------
### PHASE 5 — VALIDATION
--------------------------------------------------

Confirm findings are not statistical noise.

Out-of-Sample Test

Split data
70% in-sample
30% out-of-sample

Regress out-of-sample co-movement on in-sample similarity score.

Metric used
Spearman correlation

Circular Block Bootstrap

Block size
20 days

Number of bootstrap samples
1000

Compute 95% confidence intervals per pair.

Surrogate Data Test

Generate phase-shuffled surrogate returns.

Simulations
500

Used to construct a null distribution for λL.

Robust Redundancy Rule

Pairs are classified as Highly Redundant only if:

similarity_score > 0.70

AND all of the following agree:

Correlation signal
Lower tail dependence λL
Bear-regime correlation
Cointegration

Outputs

validation/
  validation_report.md

validation_report.md contains

Out-of-sample Spearman correlation
Bootstrap confidence intervals
Robustness flags

--------------------------------------------------
### BUILD SCHEDULE
--------------------------------------------------

Week 1
Phase 1 — Data prep, filtering, stationarity tests

Weeks 2–3
Phase 2 — Similarity signals and copula estimation

Week 4
Phase 3 — Regime detection, cointegration, Granger causality

Week 5
Phase 4 — Composite score calculation and clustering

Week 6
Phase 5 — Validation and robustness testing

--------------------------------------------------
FINAL OBJECTIVE
--------------------------------------------------

Identify economically redundant crypto assets so that portfolio transfers:

Avoid unnecessary transaction costs
Avoid false diversification
Maintain genuine exposure diversification