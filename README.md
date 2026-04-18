# Crypto Similarity Framework — Implementation Roadmap
> **Goal:** Identify and classify cryptocurrencies with similar performance behavior to avoid unnecessary fund transfers between redundant assets.

---

## Table of Contents
- [Phase 0 — Data Audit & Universe Filtering](#phase-0--data-audit--universe-filtering)
- [Phase 0.5 — Pre-Flight Validity Checks](#phase-05--pre-flight-validity-checks-mandatory)
- [Phase 1 — Return Series Construction](#phase-1--return-series-construction)
- [Phase 2 — Baseline Similarity Matrix](#phase-2--baseline-similarity-matrix)
- [Phase 3 — Copula-Based Tail Dependence](#phase-3--copula-based-tail-dependence)
- [Phase 4 — Regime-Conditional Similarity](#phase-4--regime-conditional-similarity)
- [Phase 5 — Cointegration & Lead-Lag](#phase-5--cointegration--lead-lag)
- [Phase 6 — Network Construction](#phase-6--network-construction)
- [Phase 7 — Composite Similarity Score](#phase-7--composite-similarity-score)
- [Phase 8 — Clustering & Classification](#phase-8--clustering--classification)
- [Phase 9 — Validation & Robustness](#phase-9--validation--robustness)
- [Final Deliverables](#final-deliverables)
- [What to Skip & Why](#what-to-skip--why)

---

## Phase 0 — Data Audit & Universe Filtering

> **Purpose:** Know exactly what you're working with before touching any statistics.

### 0.1 Coverage Check
- [ ] Count trading days per coin — minimum threshold: **400+ days** out of ~730
- [ ] Flag coins launched mid-period or delisted early → exclude from main analysis
- [ ] Identify coins with **price gaps > 3 consecutive days** → decide: forward-fill or drop

### 0.2 Stablecoin Removal
- [ ] Use `is_stablecoin` flag to remove all stablecoins
- [ ] Also manually check: algorithmic stablecoins (UST-type) may have `is_stablecoin = False` but behave like one until they collapse — inspect manually

### 0.3 Liquidity Filter (Amihud Illiquidity Ratio)

> ⚠️ **This is mandatory, not optional.** Illiquid coins show spurious correlation because their price barely moves — thin order books, not genuine co-movement. You will declare them redundant when the similarity is just illiquidity noise.

**Formula:**
```
ILLIQ_i = (1/T) * Σ |r_it| / Volume_USD_it
```
Where `r_it` = daily log return, `Volume_USD_it` = daily USD volume

- [ ] Compute Amihud ratio per coin over full period
- [ ] Set threshold (suggested: drop coins in top 20% most illiquid)
- [ ] Also apply hard floor: **median daily volume < $500K → exclude**
- [ ] Document how many coins survive this filter

### 0.4 Missing Value Audit
- [ ] Count `NaN` percentage per coin for `close` and `volume_usd`
- [ ] Strategy:
  - Gaps ≤ 2 days → forward fill
  - Gaps 3–7 days → flag, forward fill with warning
  - Gaps > 7 days → exclude coin from analysis

### 0.5 Expected Universe Size
```
Start:          500 coins
After coverage: ~400 coins
After stablecoins: ~370 coins  
After liquidity: ~150–250 coins   ← working universe
```

---

## Phase 0.5 — Pre-Flight Validity Checks *(Mandatory)*

> ⚠️ **These three checks determine the mathematical validity of everything downstream. Do not skip.**

### 0.5.1 Stationarity Testing per Coin

Run **both** ADF and KPSS on each coin's log return series:

| ADF Result | KPSS Result | Interpretation | Action |
|---|---|---|---|
| Reject H0 (stationary) | Fail to reject (stationary) | ✅ Stationary | Use as-is |
| Fail to reject (non-stationary) | Reject (non-stationary) | ❌ Unit root | Difference again |
| Reject H0 | Reject | ⚠️ Conflicting | → Test for fractional integration |
| Fail to reject | Fail to reject | ⚠️ Conflicting | → Test for fractional integration |

- [ ] Run ADF (with lags selected by AIC) on every coin's log returns
- [ ] Run KPSS on every coin's log returns
- [ ] Flag all coins with **conflicting results** → queue for ARFIMA test

### 0.5.2 Fractional Integration Test (ARFIMA)

> **Why this matters:** If a coin's return series has long memory with d ∈ (0, 0.5), it is neither stationary nor a random walk. Running standard correlation or copulas on it produces **mathematically invalid results**.

- [ ] For all flagged coins from 0.5.1: estimate fractional differencing parameter `d`
- [ ] Decision rule:
  - `d ≈ 0` → treat as stationary I(0)
  - `d ≈ 1` → treat as I(1), use log returns
  - `0 < d < 0.5` → apply fractional differencing before any similarity computation
- [ ] Document which coins required fractional differencing — they need separate handling

### 0.5.3 Multiple Testing Correction Setup

> ⚠️ **Non-negotiable at your scale.**

```
500 coins → 124,750 unique pairs
At α = 0.05 → ~6,237 false positives expected by pure chance
```

- [ ] Set significance framework: **Benjamini-Hochberg False Discovery Rate (FDR)**
- [ ] Chosen FDR level: `q = 0.05` (5% of declared significant pairs are false)
- [ ] Apply BH correction to **every** p-value output in all subsequent phases
- [ ] Never report a pair as "significantly similar" without BH-adjusted p-value

---

## Phase 1 — Return Series Construction

> **Purpose:** Build the clean `(T × N)` log-return matrix that feeds all downstream analysis.

### 1.1 Log Return Computation
```python
# Formula
log_return = ln(close_t / close_t-1)
```
- [ ] Compute log returns for all coins in working universe
- [ ] Shape check: result should be `(T-1) × N` matrix, no `NaN` in first row

### 1.2 Fat Tail Characterization
- [ ] Fit **Student-t distribution** to each coin's return series
- [ ] Extract degrees-of-freedom (`ν`) per coin — needed for copula fitting in Phase 3
- [ ] Flag coins with `ν < 4` (extreme fat tails) — these need extra care in copula selection

### 1.3 Structural Break Detection

> **Purpose:** Define analysis subperiods so similarity is computed within stable regimes, not across regime changes.

- [ ] Run **Zivot-Andrews test** on log-price series per coin (detects single endogenous breakpoint)
- [ ] Run **Bai-Perron test** for multiple breakpoints — expected breaks in crypto:
  - FTX collapse: Nov 2022
  - Bitcoin ETF approval: Jan 2024
  - Any coin-specific events
- [ ] Compile a **master list of break dates** across the universe
- [ ] Define subperiods: e.g., `Period 1`, `Period 2`, `Period 3` based on common break dates

### 1.4 Output of Phase 1
```
returns_matrix.parquet       → shape (T × N), log returns, clean
coin_metadata.csv            → coin_id, amihud_ratio, nu_param, break_dates, d_param
subperiod_labels.csv         → date → period label
```

---

## Phase 2 — Baseline Similarity Matrix

> **Purpose:** Establish correlation benchmark and sanity-check the data before advanced methods.

### 2.1 Static Correlation
- [ ] Compute **Pearson** correlation matrix across all N coins (full period)
- [ ] Compute **Spearman** correlation matrix (rank-based, more robust to outliers)
- [ ] Sanity check: BTC–ETH correlation should be > 0.7 — if not, debug upstream

### 2.2 Rolling Correlation
- [ ] Rolling **30-day** Pearson correlation for all pairs
- [ ] Rolling **90-day** Pearson correlation for all pairs
- [ ] Visualize distribution of correlations over time → confirms time-varying nature

### 2.3 BTC-Beta Adjusted Correlation
- [ ] Regress each coin on BTC returns → extract residuals
- [ ] Compute correlation on **residuals** (partial out BTC market factor)
- [ ] This separates: "they move together because of BTC" vs. "they move together independently"
- [ ] Both matter but must be distinguished for cluster quality

### 2.4 First-Pass Hierarchical Clustering
- [ ] Cluster on Spearman correlation matrix (1 - |ρ| as distance)
- [ ] Plot dendrogram → first visual of natural crypto groupings
- [ ] This is your **baseline to beat** with advanced methods

---

## Phase 3 — Copula-Based Tail Dependence

> **Purpose:** Answer "do these coins crash together?" — the most critical similarity dimension for fund transfer decisions.

### 3.1 Probability Integral Transform
- [ ] Transform each coin's returns to uniform marginals using empirical CDF
- [ ] This isolates the **dependence structure** from the marginal distributions

### 3.2 Bivariate Copula Fitting

For each pair in working universe:

| Copula | What It Captures | Your Use |
|---|---|---|
| **Gaussian** | Symmetric linear dependence | Baseline |
| **Clayton** | Lower tail dependence (λL) | ⭐ Crash co-movement — primary |
| **Gumbel** | Upper tail dependence (λU) | Rally co-movement |
| **Joe-Clayton (SJC)** | Asymmetric: λU ≠ λL | Full picture |

- [ ] Fit all four copulas per pair using MLE
- [ ] Select best fit per pair using **AIC / BIC**
- [ ] Extract **λL (lower tail dependence coefficient)** per pair → crash similarity score
- [ ] Extract **λU (upper tail dependence coefficient)** per pair → rally similarity score
- [ ] Start with **top 50 most liquid coins** before scaling to full universe

> **Scale note:** 124,750 pairs is computationally heavy. Use parallel processing (`joblib`) and batch by cap tier.

### 3.3 Key Output
```
tail_dependence_matrix_lower.parquet    → λL per pair (crash similarity)
tail_dependence_matrix_upper.parquet    → λU per pair (rally similarity)
copula_aic_best.csv                     → best-fit copula model per pair
```

### 3.4 Interpretation Rule
```
λL > 0.5  → High crash similarity  → strong redundancy signal
λL 0.3–0.5 → Moderate             → context-dependent
λL < 0.3  → Low crash similarity  → NOT redundant in bear markets
```

---

## Phase 4 — Regime-Conditional Similarity

> **Purpose:** Verify that similarity holds across market regimes — especially bear/crash. A pair that's only similar in bull markets is NOT redundant.

### 4.1 Market Regime Identification
- [ ] Fit **2-state Markov Regime Switching model** on BTC log returns
  - State 1: Low volatility / Bull
  - State 2: High volatility / Bear-Crash
- [ ] Try 3-state model (Bull / Sideways / Bear) and compare via log-likelihood
- [ ] Extract daily **regime probabilities** via Hamilton Filter
- [ ] Label each day: assign to dominant regime (probability > 0.65)

### 4.2 Regime-Conditional Correlation
- [ ] Split return matrix by regime labels
- [ ] Compute Pearson + Spearman correlation **within each regime** for all pairs
- [ ] Key comparison:

```
ρ_bull  = correlation during bull regime
ρ_bear  = correlation during bear/crash regime

If ρ_bear >> ρ_bull  → assets converge in crises (dangerous false diversification)
If ρ_bull >> ρ_bear  → bull-only similarity → NOT truly redundant
If both high         → structurally redundant ✅
```

### 4.3 Regime Stability Score
- [ ] For each pair: compute `|ρ_bull - ρ_bear|` → **regime stability gap**
- [ ] Small gap → similarity is regime-stable → stronger redundancy signal
- [ ] Large gap → similarity is regime-dependent → weaker redundancy signal

---

## Phase 5 — Cointegration & Lead-Lag

> **Purpose:** (1) Detect persistent long-run relationships. (2) Rank assets within clusters to identify which to hold.

### 5.1 Standard Cointegration (Engle-Granger)
- [ ] For all pairs with rolling correlation > 0.6: run Engle-Granger cointegration test
- [ ] Apply BH-FDR correction to all p-values
- [ ] Cointegrated pairs → strong redundancy candidate (log prices move together long-run)

### 5.2 Threshold Cointegration (TVECM)

> **Why over standard cointegration:** Standard cointegration says "the spread mean-reverts." TVECM says "it only mean-reverts *outside a neutral band*." For fund transfer decisions, you need to know: if A and B diverge, does the market force them back?

- [ ] For cointegrated pairs: estimate TVECM → extract neutral band width
- [ ] Narrow band + fast reversion → very strong redundancy
- [ ] Wide band + slow reversion → weaker redundancy (they can drift a long time)
- [ ] Run **MTAR** to check asymmetry: does spread correct faster when widening vs. narrowing?

### 5.3 Lead-Lag via Granger Causality
- [ ] For each cluster identified in baseline clustering: run pairwise Granger causality
- [ ] Apply BH-FDR correction
- [ ] Identify **leader coin** in each cluster:
  - Coin that Granger-causes others but is not caused by them
  - Most liquid coin with highest market cap (tiebreaker)

> **Transfer rule implication:** Within a cluster, always hold the leader. Moving funds from leader → follower gives lagged exposure to the same signal with higher slippage.

---

## Phase 6 — Network Construction

> **Purpose:** Visualize the full redundancy structure and identify asset groupings at the ecosystem level.

### 6.1 GLASSO Partial Correlation Network
- [ ] Compute **L1-regularized precision matrix** (GLASSO) on return matrix
- [ ] Convert to partial correlation network
- [ ] Removes spurious indirect connections ("A and C look similar only because both correlate with B")
- [ ] Tune regularization parameter `λ` via cross-validation

### 6.2 Minimum Spanning Tree on λL
- [ ] Build MST where edge weights = **lower tail dependence (λL)** from Phase 3
- [ ] Higher λL = stronger crash similarity = shorter edge in MST
- [ ] MST shows the **backbone of crash-time redundancy**
- [ ] Nodes at the periphery = most unique assets (lowest redundancy)
- [ ] Nodes in the core = most substitutable (highest redundancy)

### 6.3 Community Detection
- [ ] Apply Louvain community detection on GLASSO network
- [ ] Apply Louvain on λL-MST separately
- [ ] Compare communities from both → where they agree = **high-confidence clusters**
- [ ] Where they disagree → flag for manual review

---

## Phase 7 — Composite Similarity Score

> **Purpose:** Combine all signals into a single interpretable redundancy score per pair.

### 7.1 Score Components

| Component | Source | Weight (suggested) |
|---|---|---|
| Rolling Correlation (90d) | Phase 2 | 20% |
| BTC-adjusted correlation | Phase 2 | 10% |
| Lower Tail Dependence λL | Phase 3 | 25% |
| Bear-regime correlation | Phase 4 | 20% |
| Cointegration (binary + speed) | Phase 5 | 15% |
| GLASSO partial correlation | Phase 6 | 10% |

> **Note:** Weights are tunable. Validate against out-of-sample co-movement in Phase 9.

### 7.2 Composite Score Formula
```
Similarity_Score(A,B) = Σ w_i * normalized_component_i

Where each component is min-max normalized to [0, 1]
```

### 7.3 Redundancy Classification

| Score Range | Classification | Transfer Recommendation |
|---|---|---|
| 0.80 – 1.00 | 🔴 Highly Redundant | Avoid transfer — near-zero diversification benefit |
| 0.60 – 0.79 | 🟠 Moderately Redundant | Transfer adds marginal benefit only |
| 0.40 – 0.59 | 🟡 Partially Similar | Sector overlap but meaningful differences |
| 0.00 – 0.39 | 🟢 Distinct | Transfer adds genuine diversification |

---

## Phase 8 — Clustering & Classification

> **Purpose:** Group coins into clusters where intra-cluster transfers are redundant.

### 8.1 Hierarchical Clustering on Composite Score
- [ ] Use `(1 - Similarity_Score)` as distance matrix
- [ ] Method: **Ward linkage** (minimizes within-cluster variance)
- [ ] Plot dendrogram

### 8.2 Optimal Cluster Count
- [ ] **Silhouette score** across k = 5 to 30 clusters
- [ ] **Calinski-Harabasz index**
- [ ] Dendrogram cut-point inspection
- [ ] Choose k that maximizes silhouette while producing interpretable clusters

### 8.3 Cluster Labeling
- [ ] Assign descriptive label per cluster based on dominant coin type:
  - e.g., `Layer-1 Smart Contracts`, `DeFi Protocols`, `Meme Coins`, `Exchange Tokens`
- [ ] Flag mixed clusters for review

### 8.4 Representative Asset per Cluster
For each cluster, select the representative (the one to "hold"):
- [ ] Highest median daily volume (most liquid)
- [ ] Longest history (most data)
- [ ] Lowest Amihud illiquidity ratio
- [ ] Highest market cap (tiebreaker)
- [ ] Verify it is the **Granger-leader** from Phase 5 — should match

### 8.5 Temporal Stability Check
- [ ] Re-run clustering on each subperiod from Phase 1.3
- [ ] Measure cluster membership changes across subperiods
- [ ] **Stable cluster** = same coins grouped together across 3+ subperiods
- [ ] Unstable cluster = lower confidence → flag in output

---

## Phase 9 — Validation & Robustness

> **Purpose:** Separate findings from statistical noise. This is what separates research from guesswork.

### 9.1 Out-of-Sample Predictive Validity
- [ ] Split: **70% in-sample** (estimation), **30% out-of-sample** (validation)
- [ ] Claim: "High similarity score today → high co-movement in next 30/60 days"
- [ ] Test: regress OOS co-movement on in-sample similarity score
- [ ] Metric: Spearman rank correlation between similarity score and OOS realized correlation

### 9.2 Block Bootstrap Confidence Intervals

> Standard bootstrap is invalid for time series (breaks temporal dependence). Use stationary block bootstrap.

- [ ] Apply **circular block bootstrap** with block length = 20 days
- [ ] Bootstrap 1,000 samples
- [ ] Compute 95% CI for composite similarity score per pair
- [ ] Report: point estimate ± CI for every "highly redundant" pair

### 9.3 Subperiod Robustness
For every high-confidence redundant pair, verify finding holds across:
- [ ] Pre-break period (Phase 1 subperiod 1)
- [ ] Post-break period (Phase 1 subperiod 2+)
- [ ] Bull regime only
- [ ] Bear regime only

```
Robustness rule: A pair is only classified "Highly Redundant" 
if similarity score > 0.70 in ALL subperiods tested.
```

### 9.4 Surrogate Data Testing (for Copula Results)
- [ ] Phase-shuffle each return series 500 times → surrogate datasets
- [ ] Recompute λL on surrogates → null distribution
- [ ] Actual λL must exceed 95th percentile of null → genuine tail dependence confirmed

### 9.5 Alternative Measure Agreement Check
For every "Highly Redundant" classification, verify:
- [ ] ✅ High rolling correlation (Phase 2)
- [ ] ✅ High λL from copula (Phase 3)
- [ ] ✅ High bear-regime correlation (Phase 4)
- [ ] ✅ Cointegrated (Phase 5)

> **Rule:** All 4 must agree. If only 2–3 agree → downgrade to "Moderately Redundant."

---

## Final Deliverables

```
📦 outputs/
├── 01_universe_filtered.csv              → Final coin list post all filters
├── 02_returns_matrix.parquet             → (T × N) log return matrix
├── 03_coin_metadata.csv                  → amihud, nu, d_param, break_dates per coin
├── 04_correlation_matrix_full.parquet    → Pearson + Spearman, full period
├── 05_correlation_matrix_btcadj.parquet  → BTC-beta adjusted correlations
├── 06_tail_dependence_lower.parquet      → λL matrix (crash similarity)
├── 07_tail_dependence_upper.parquet      → λU matrix (rally similarity)
├── 08_regime_labels.csv                  → date → bull/bear label
├── 09_regime_conditional_corr.parquet    → ρ_bull, ρ_bear per pair
├── 10_cointegration_results.csv          → test stat, p-value (BH-adjusted), TVECM band
├── 11_granger_causality.csv              → leader/follower per cluster
├── 12_glasso_network.graphml             → partial correlation network
├── 13_mst_tail_dependence.graphml        → λL minimum spanning tree
├── 14_composite_similarity_matrix.parquet → final score per pair
├── 15_cluster_assignments.csv            → coin → cluster_id, cluster_label
├── 16_cluster_representatives.csv        → cluster_id → representative coin
├── 17_transfer_avoidance_rules.csv       → pair → score, classification, recommendation
└── 18_validation_report.md              → OOS results, bootstrap CIs, robustness
```

---

## What to Skip & Why

| Method | Framework Layer | Reason to Skip |
|---|---|---|
| Vine Copulas | Layer 2 | Overkill — bivariate copulas sufficient for pairwise classification |
| Transfer Entropy full stack | Layer 3 | Causality lite (Granger) is enough for ranking within clusters |
| HF Realized Measures | Layer 5 | No intraday data available |
| Kyle's Lambda | Layer 5 | Requires order book data — not in your dataset |
| On-Chain Metrics | Layer 8 | Separate data source; add in v2 if needed |
| Persistence Homology (TDA) | Layer 6 | Research-grade, diminishing returns for classification goal |
| CCM / PCMCI | Layer 3 | Complexity science tools — beyond scope for similarity classification |
| ΔCoVaR Network | Layer 6 | Systemic risk focus, not similarity focus |

---

## Build Schedule

| Week | Phase | Key Output |
|---|---|---|
| 1 | Phase 0 + 0.5 | Clean universe, validity checks pass |
| 2 | Phase 1 | Returns matrix, break dates, subperiod labels |
| 3 | Phase 2 | Baseline correlation matrices, first clustering |
| 4 | Phase 3 | Tail dependence matrices (λL, λU) |
| 5 | Phase 4 | Regime labels, regime-conditional correlations |
| 6 | Phase 5 | Cointegration results, Granger leaders |
| 7 | Phase 6 | GLASSO network, λL-MST, communities |
| 8 | Phase 7 + 8 | Composite score, clusters, transfer rules |
| 9 | Phase 9 | Validation, bootstrap CIs, final report |

---

*Framework adapted from: Advanced Crypto Similarity Research Framework. Scoped for goal: identify redundant assets to avoid unnecessary fund transfers.*
