# Crypto Intelligence Dashboard — User Manual

**Version:** 1.0  
**Stack:** Streamlit · Polars · Plotly  
**Data:** HuggingFace — `shekharbiswas/crypto-indicators`

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Sidebar Controls](#sidebar-controls)
4. [KPI Header Row](#kpi-header-row)
5. [Tab 1 — Market Overview](#tab-1--market-overview)
6. [Tab 2 — Tier Breakdown](#tab-2--tier-breakdown)
7. [Tab 3 — Coin Deep Dive](#tab-3--coin-deep-dive)
8. [Tab 4 — Return Similarity](#tab-4--return-similarity)
9. [Tab 5 — Regime Similarity](#tab-5--regime-similarity)
10. [Tab 6 — Forward Return Lab](#tab-6--forward-return-lab)
11. [Glossary](#glossary)
12. [Known Limitations](#known-limitations)

---

## Overview

Crypto Intelligence is a multi-tab analytical dashboard covering 688 cryptocurrencies with daily OHLCV data and 70+ pre-computed technical indicators. The dashboard is designed for three use cases:

- **Market scanning** — quickly identify which cap tiers and coins are outperforming over a selected period
- **Pair and similarity analysis** — find coins that move together historically (return similarity) or are in the same technical state today (regime similarity)
- **Base-rate research** — understand how a coin has historically performed after entering a specific RSI + ADX regime

Data is loaded once on startup and cached for the session. All filtering and computation happens in-memory using Polars and Pandas.

---

## Getting Started

### Running Locally

```bash
pip install streamlit polars pandas plotly scipy huggingface_hub fsspec datasets
streamlit run app.py
```

First load downloads the full dataset from HuggingFace (~150MB parquet). Subsequent runs use Streamlit's cache and load instantly.

### Running on Streamlit Cloud

Add the following to `requirements.txt` in the repository root:

```
streamlit
polars
pandas
plotly
scipy
numpy
huggingface_hub>=0.21
fsspec
datasets
```

Push to GitHub and connect to Streamlit Community Cloud. The app will deploy automatically.

### Data Source

The dataset is hosted at:

```
hf://datasets/shekharbiswas/crypto-indicators/crypto_with_indicators.parquet
```

It contains daily OHLCV rows for 688 non-stablecoin cryptocurrencies from 2020 onwards, enriched with the following indicator families:

- **Trend:** EMA (9/21/50/100/200), SMA (50/200), Supertrend, Parabolic SAR, Ichimoku Cloud
- **Momentum:** RSI, Stochastic K/D, Williams %R, CCI, ROC (9/14/21), TSI, MACD
- **Volatility:** Bollinger Bands, Keltner Channels, Donchian Channels, ATR
- **Volume:** OBV, A/D Line, CMF, MFI, Volume ROC, VWAP
- **Directional:** ADX, +DI, −DI, Aroon Up/Down/Oscillator
- **Pattern:** Higher Highs, Higher Lows, Pivot, R1/R2, S1/S2
- **Labels:** Next 1d / 2d / 3d / 5d / 7d forward returns, Surge Score

---

## Sidebar Controls

The sidebar is global — every change immediately affects all six tabs and the KPI header row.

### Return Period

Selects the historical window used to compute returns across the dashboard.

| Option | Description |
|--------|-------------|
| 1M | Last 30 days |
| 3M | Last 90 days |
| 6M | Last 180 days |
| 1Y | Last 365 days |
| 3Y | Last 3 years |
| 4Y | Last 4 years |
| All | Full history since coin listing |

Coins that were listed after the selected cutoff date are **excluded** from period-return metrics. The KPI card "Coins w/ data" shows exactly how many coins qualify for the selected period.

### Cap Tiers

Filters which market-capitalisation segments are included in all charts and tables.

| Tier | Market Cap Range |
|------|-----------------|
| MEGA | > $100B |
| LARGE | $10B – $100B |
| MID | $1B – $10B |
| SMALL | $100M – $1B |
| MICRO | < $100M |

Unchecking a tier removes it from all visualisations immediately. Tiers can be combined freely.

### Volatility Clip

Clips the x-axis maximum on the Risk vs Return scatter chart (Tab 1). Coins with daily volatility above the clip value are pulled to the clip boundary rather than plotted outside the chart area. This prevents a handful of extreme micro-caps from collapsing the scale and making all other coins unreadable.

Default: `0.25`. Range: `0.05 – 0.50`.

### Max Return % Clip

Clips the y-axis maximum on the Risk vs Return scatter chart. Same logic as Volatility Clip — prevents extreme outlier returns (e.g. +50,000%) from destroying the chart scale.

Default: `2000`. Range: `200 – 5000`.

---

## KPI Header Row

Six metric cards appear at the top of every tab, always reflecting the currently selected period and cap tiers.

| Card | What it shows | Changes with period? |
|------|--------------|----------------------|
| Total Mkt Cap | Sum of last-known market caps across selected tiers | No — always latest snapshot |
| Median Ret | Median return % across all qualifying coins | Yes |
| Best | Symbol of the top-performing coin | Yes |
| Worst | Symbol of the worst-performing coin | Yes |
| % Positive | Share of coins with a positive return | Yes |
| Coins w/ data | Count of coins with sufficient history for the period | Yes |

Hover over the `?` icon on each card for a detailed tooltip explanation.

---

## Tab 1 — Market Overview

### Risk vs Return Scatter

The primary market map. Each bubble represents one coin plotted on:

- **X-axis:** Daily return volatility (σ) — how much the price typically moves per day
- **Y-axis:** Return % for the selected period
- **Bubble size:** Log-transformed market cap — larger bubbles are higher market cap

**Reading the chart:**

The chart is divided into four quadrants by two reference lines:

- **Gold dashed vertical line** — median volatility of all displayed coins. Coins to the right are riskier than the median.
- **Dotted horizontal line at y=0** — break-even. Coins above are profitable over the period.

The ideal zone is **top-left** (low risk, high return). The worst zone is **bottom-right** (high risk, negative return).

**Hovering** over any bubble shows the full return breakdown across all periods (1M through 4Y), volatility, Sharpe proxy, and market cap.

### Winners Table

Expanding the "Winners Table" section beneath the chart shows a sortable, styled data table of all coins in the current selection, ranked by the active return period. The active period column is highlighted in gold.

A quick **Top 5 / Bottom 5** summary appears below the full table.

---

## Tab 2 — Tier Breakdown

Three bar charts compare the five cap tiers side by side:

- **Left — Coin Count:** How many coins exist in each tier within the current selection
- **Centre — Avg Return:** Average return for the selected period per tier. Green bars = positive average, red = negative
- **Right — Median Volatility:** Colour-scaled from blue (low vol) to pink (high vol)

### Return Distribution Violin Plot

Below the bar charts, a violin plot shows the **full distribution** of returns per tier — not just the average. Wide sections of a violin mean many coins posted returns at that level. The box inside each violin shows the interquartile range (25th–75th percentile). Outlier dots appear beyond the whiskers.

This chart answers the question a simple average cannot: are gains broadly distributed or concentrated in a few coins?

---

## Tab 3 — Coin Deep Dive

Single-coin analysis across price action, momentum, volume, and current regime state.

### Controls

| Control | Options | Description |
|---------|---------|-------------|
| Coin selector | All coins in selected tiers | Sorted by market cap descending |
| Chart type | Line / Candlestick / OHLC | Visual style of the price panel |
| Date range | 1M / 3M / 6M / 1Y / 2Y / 3Y / All | History window for the chart |

### 4-Panel Chart

**Panel 1 — Price**

Shows close price (Line mode) or full OHLC (Candlestick/OHLC mode). In Line mode, a 20-day moving average overlay appears in gold when at least 20 data points exist in the selected range.

**Panel 2 — RSI**

Relative Strength Index (14-period). Key zones:
- Above 70 (gold shading) — overbought: price may be extended, mean-reversion risk increases
- Below 30 (red shading) — oversold: price may be depressed, potential recovery zone
- 30–70 — neutral: no directional edge from RSI alone

**Panel 3 — MACD**

Three components displayed together:
- **MACD line** (teal) — fast minus slow EMA
- **Signal line** (gold dashed) — 9-period EMA of MACD
- **Histogram** (bars) — gap between MACD and signal; teal bars = bullish momentum accelerating, red bars = bearish

A MACD cross above the signal line with a growing histogram suggests momentum is building to the upside and vice versa.

**Panel 4 — Volume**

Daily trading volume in USD. Bars are coloured teal on up-days (close > open) and red on down-days. Volume spikes on up-days confirm buyer conviction; spikes on down-days suggest distribution.

### Regime State Cards

Six cards beneath the chart summarise the coin's **current** technical posture in a single glance.

| Card | Signal | Interpretation |
|------|--------|---------------|
| RSI Regime | OVERSOLD / NEUTRAL / OVERBOUGHT | Based on latest RSI reading |
| Trend Strength | RANGING / TRENDING / STRONG TREND | Based on ADX level |
| Trend Direction | BULLISH / BEARISH / MIXED | Requires Supertrend AND PSAR to agree |
| BB Position | NEAR LOWER BAND / MID BAND / NEAR UPPER BAND | Bollinger Band %B position |
| EMA Stack | BULL STACK / BEAR STACK / MIXED | EMA 9 > EMA 21 > EMA 50 alignment |
| Surge Score | Numeric | Composite momentum/breakout score |

When 4 or more cards agree (e.g. all bullish), conviction is considered high. Mixed signals indicate a transitional or choppy regime with no clear directional edge.

### Raw Data Expander

Expanding "Raw OHLCV + Indicators" shows a table of the most recent rows for the selected coin with OHLCV, RSI, MACD, ADX, BB%, and Surge Score columns.

---

## Tab 4 — Return Similarity

Identifies which coins have historically moved most like the selected anchor coin, based on **daily log return correlation**.

### Controls

| Control | Description |
|---------|-------------|
| Anchor coin | The reference coin to find similar matches for |
| Correlation window | Date range over which Pearson correlation is computed (3M to All) |
| Show seasonal heatmaps | Toggle month × year return heatmaps on/off |
| Coins to overlay | How many of the top matches to show on the normalised price chart |

### How Similarity is Measured

**Pearson Correlation (r)** is computed on daily log returns over the selected window. A value of:
- `r > 0.8` — strongly correlated: the two coins tend to rise and fall together on the same days
- `r 0.5–0.8` — moderately correlated
- `r < 0.5` — weak: the co-movement is unreliable

**Same-Dir %** is a non-parametric check: out of all shared trading days, what percentage did both coins move in the same direction? A value of 50% is random; 75%+ is meaningful.

**p-value** tests statistical significance. Values below 0.05 mean the correlation is unlikely to be due to chance.

### KPI Cards

| Card | Meaning |
|------|---------|
| Best Match | The single most correlated coin |
| Avg Top-10 Corr | Mean Pearson r across all 10 results |
| Avg Same-Dir % | Average directional agreement across top 10 |
| Significant (p<0.05) | How many of the 10 correlations are statistically reliable |

### Correlation Bar Chart

Horizontal bars ranked by Pearson r, colour-scaled from deep purple (low) to gold (high = 1.0). Hovering shows full details including p-value and number of shared observations.

### Normalised Price Overlay

All selected coins are rebased to 100 at the start of the window. This removes price-scale differences and makes co-movement visually readable. A high Pearson r should produce overlapping lines. Divergences show where and when the correlation broke down.

### Rolling 90-Day Correlation

The most actionable chart in this tab. Rather than a single r value for the whole window, this shows how the correlation evolved over time. Key patterns to look for:

- **Stable line near 0.8+** — structural relationship, reliable for hedging or pair trading
- **Correlation collapsing during drawdowns** — regime-dependent relationship, less reliable
- **Correlation that inverts** — the coins diverge under stress, potential diversification value

The gold dashed line at r = 0.7 is a reference threshold.

### Seasonal Return Heatmaps

Month × Year grids for the anchor coin and its best match. Each cell shows the total return for that calendar month. Reading across a row (e.g. all January cells) reveals whether the coin has a consistent seasonal bias in that month.

A **Δ Return heatmap** below shows the difference between the two coins month by month. Teal = anchor outperformed, red = anchor underperformed.

---

## Tab 5 — Regime Similarity

Identifies which coins are in the **same technical state right now** as the selected anchor, regardless of historical return correlation.

### How It Differs from Return Similarity

| | Return Similarity (Tab 4) | Regime Similarity (Tab 5) |
|---|---|---|
| Question | Which coins moved together historically? | Which coins are technically co-positioned today? |
| Lookback | User-selected window (months to years) | Latest snapshot only |
| Method | Pearson correlation on log returns | Cosine similarity on 11 normalised indicator features |
| Use case | Pair trading, hedging, portfolio construction | Regime-aware entries, rotation signals |

### The 11-Feature Technical Vector

Each coin's latest technical state is described by:

1. RSI — momentum oscillator
2. BB% — Bollinger Band position (0 = lower band, 1 = upper band)
3. ADX — trend strength
4. +DI — bullish directional pressure
5. −DI — bearish directional pressure
6. Supertrend Direction — trend signal (+1 / −1)
7. Parabolic SAR Trend — trend signal (+1 / −1)
8. CMF — Chaikin Money Flow
9. MFI — Money Flow Index
10. Aroon Oscillator — trend direction and strength
11. EMA Stack — alignment of EMA 9/21/50 (+1 bull / −1 bear / 0 mixed)

All features are z-score normalised across the full universe before computing cosine similarity, so scale-dependent indicators (e.g. ADX 0–100) do not dominate scale-independent ones (e.g. Supertrend ±1).

### Anchor Regime State Cards

Six cards show the anchor coin's current readings across the key signals, identical in format to the Coin Deep Dive tab regime cards.

### Cosine Similarity Bar Chart

Ranked list of the top N coins most similar to the anchor in technical space. A cosine score of 1.0 means perfect technical alignment across all 11 features.

### Feature Radar

A spider/radar chart overlaying the anchor coin (gold) against its best regime match (teal). Each spoke is one of the 8 primary features, normalised 0→1 within the universe. Overlapping filled shapes confirm technical co-positioning. Spokes that diverge reveal exactly which indicators differ despite an overall high cosine score.

### Practical Use Cases

- **Pair trading:** Two coins in the same regime that historically diverge in returns present a relative value opportunity
- **Portfolio diversification:** Avoid holding two coins with near-identical regime vectors — they will react identically to macro shocks
- **Sector rotation:** Coins that have recently moved from one regime cluster to another are in transition — monitor for follow-through

---

## Tab 6 — Forward Return Lab

A conditional base-rate analysis that answers: *"Historically, when this coin was in a similar RSI + ADX regime to today, what did its returns look like over the next 1 to 7 days?"*

### Controls

| Control | Description |
|---------|-------------|
| Coin | The coin to analyse |
| RSI tolerance ± | Match historical dates where RSI was within this band of today's RSI |
| ADX tolerance ± | Match historical dates where ADX was within this band of today's ADX |

Tighter tolerances produce fewer but more precise historical matches. Wider tolerances produce more matches but noisier distributions. A minimum of 15–20 matches is recommended for the distribution to be reliable.

### Context Bar

Below the controls, a grey info line shows the current RSI, ADX, and Surge Score values for the selected coin alongside the exact search bands being applied.

### KPI Cards

| Card | Meaning |
|------|---------|
| Matched Dates | Number of historical days found in the regime band |
| Median 1d Fwd | Median next-day return across all matches |
| Median 5d Fwd | Median 5-day forward return across all matches |
| % Positive 5d | Share of matches where the 5-day return was positive |

### Forward Return Distribution Box Plot

Five boxes showing the distribution of forward returns at each horizon (1d through 7d). Each box shows:
- **Centre line** — median return
- **Box edges** — 25th and 75th percentile
- **Whiskers** — 5th and 95th percentile
- **Dots** — outliers beyond the whiskers
- **Colour** — teal if median is positive, red if negative

A box sitting entirely above zero and growing wider at longer horizons suggests momentum continuation in this regime. A box straddling zero means the regime has historically been inconclusive.

### Surge Score vs 5d Return Scatter

Each dot is one matched historical date. The x-axis is the surge score on that date; the y-axis is the 5-day return that followed. An OLS trend line is fitted with its r value displayed.

- `r > 0.3` — surge score has incremental signal in this regime
- `r > 0.5` — strong for a single indicator
- Flat or negative slope — surge score is not informative for this coin in this regime

### Matched Dates Table

Expanding the expander at the bottom of the tab shows all matched historical rows with their RSI, ADX, Surge Score, and actual forward returns — useful for inspecting individual regime entries manually.

---

## Glossary

| Term | Definition |
|------|-----------|
| Log Return | Natural log of price ratio: ln(close_t / close_{t-1}). Additive and symmetric, preferred over simple returns for statistical analysis |
| Sharpe Proxy | Mean daily log return divided by its standard deviation. A rough risk-adjusted performance metric — higher is better |
| Cap Tier | Market capitalisation segment: MEGA > LARGE > MID > SMALL > MICRO |
| Pearson r | Correlation coefficient ranging −1 to +1. Measures linear co-movement of two return series |
| Cosine Similarity | Dot product of two normalised vectors. Measures directional alignment in feature space regardless of magnitude |
| Surge Score | Composite momentum/breakout score aggregating multiple signals. Higher values indicate several indicators simultaneously elevated |
| Regime | A combination of technical indicator readings that describes the current market state of a coin |
| Base Rate | Historical frequency of an outcome given a specific condition — not a prediction, but a prior probability |
| ADX | Average Directional Index. Measures trend strength on a 0–100 scale. < 20 = ranging, 20–40 = trending, > 40 = strong trend |
| Supertrend | Trend-following indicator that signals +1 (bullish) or −1 (bearish) based on ATR-adjusted bands |
| PSAR | Parabolic Stop and Reverse. Signals trend direction; agrees with Supertrend for a clean directional read |
| EMA Stack | Alignment of EMA 9 > EMA 21 > EMA 50 (bull stack) or EMA 9 < EMA 21 < EMA 50 (bear stack) |
| BB% | Bollinger Band percent — position of price within the band. 0 = at lower band, 1 = at upper band |
| CMF | Chaikin Money Flow. Positive = net buying pressure, negative = net selling pressure |
| MFI | Money Flow Index. Volume-weighted RSI. > 80 overbought, < 20 oversold |

---

## Known Limitations

- **Total Mkt Cap is static** — it always reflects the latest market cap snapshot regardless of the selected return period. It is not a historical market cap figure.
- **Period returns require sufficient history** — coins listed after the period cutoff are excluded. Short-history coins only appear under the "All" period.
- **Regime snapshot is point-in-time** — Tabs 5 and 6 use the latest available data row per coin. If the dataset is not refreshed, these tabs reflect the state at the last data update.
- **Pearson correlation is linear** — it may understate relationships that are non-linear or regime-dependent. Use the Rolling 90-Day chart in Tab 4 to check stability.
- **Forward Return Lab is not predictive** — base rates are historical summaries. Past regime outcomes do not guarantee future returns.
- **First load is slow** — the full parquet file (~150MB) is downloaded from HuggingFace on the first run. Subsequent runs use Streamlit's cache and are instant.

---

*Crypto Intelligence Dashboard — Built with Streamlit, Polars, Plotly*  
*Data: HuggingFace — shekharbiswas/crypto-indicators*