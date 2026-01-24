# Cryptocurrency Selection Logic for Similarity Analysis

This document outlines a **structured, research-oriented framework** for selecting a high-quality universe of cryptocurrencies suitable for **similarity analysis, clustering, correlation studies, and portfolio research**.

The goal is to reduce noise, ensure data integrity, and preserve **economic and sectoral relevance**, resulting in a manageable and statistically robust token universe.



## Overview

- **Starting universe**: ~14,000 listed cryptocurrencies  
- **Final universe**: **80–120 tokens**
- **Use cases**:
  - Similarity / clustering analysis
  - Correlation & volatility studies
  - Portfolio construction & rotation
  - Regime / sector behavior analysis



## Part 1: Multi-Stage Filtering Logic

### Stage 1: Hard Filters (Eliminates ~95% of tokens)

These filters enforce **minimum economic and data quality standards**.



### 1.1 Market Capitalization Threshold

**Criterion**
- Market cap > **$100M**  
  *(Adjustable to $50M for higher risk tolerance or $250M for conservatism)*

**Rationale**
- Ensures economic relevance  
- Removes micro-cap tokens with unreliable price discovery

**Impact**
- ~14,000 → **500–800 tokens**



### 1.2 Liquidity Requirements

**Criterion**
- Average daily trading volume > **$1M** (last 30 days)  
  **OR**
- Listed on **≥ 3 major exchanges**:
  - Binance
  - Coinbase
  - Kraken
  - OKX
  - Bybit

**Rationale**
- Reduces slippage and manipulation risk  
- Low-liquidity tokens distort similarity metrics

**Impact**
- **300–500 tokens**



### 1.3 Data Continuity

**Criterion**
- ≥ **12 months** of continuous daily price history  
- ≤ **5% missing data points**  
- No trading halts > **7 consecutive days**

**Rationale**
- Correlation and volatility estimates require consistent data  
- Gaps lead to unstable similarity scores

**Impact**
- **250–400 tokens**



### 1.4 Exchange Quality Filter

**Criterion**
- Listed on at least one **Tier-1 exchange**:
  - Binance
  - Coinbase
  - Kraken
  - Gemini

**Rationale**
- Tier-1 exchanges provide implicit quality screening  
- Higher reporting and listing standards

**Impact**
- **200–300 tokens**



## Stage 2: Soft Filters (Quality Refinement)

These filters improve **data cleanliness and behavioral realism**.

---

### 2.1 Price Stability Filter

**Criterion**
- Exclude tokens with:
  - >50% of days at zero volume  
  - Repeated unchanged daily prices

**Rationale**
- Signals abandoned or inactive projects



### 2.2 Outlier Removal

**Criterion**
- Exclude tokens with:
  - Daily returns > +90%  
  - Daily drops < −90%

**Rationale**
- Often caused by bad data, forks, or manipulation  
- Skews similarity metrics



### 2.3 Recency Filter

**Criterion**
- Positive trading volume in the **last 7 days**

**Rationale**
- Confirms active market participation



## Stage 3: Economic Relevance (Final ~100–150 Tokens)



### 3.1 Sector Representation

- Classify tokens into predefined crypto sectors (see Part 2)
- Select **Top N tokens per sector** by market cap or usage

**Goal**
- Avoid overrepresentation of one narrative (e.g., only L1s)

---

### 3.2 Correlation Diversity Check

**Criterion**
- Within each sector, remove tokens with:
  - Correlation > **0.95** to larger-cap peers

**Rationale**
- Removes redundant assets  
- Improves clustering resolution



## Part 2: Sector-Based Selection Logic

### Why Sector Classification Matters

Crypto sectors differ in:
- **Use cases**
- **Revenue models**
- **Regulatory exposure**
- **Technology stacks**

Sector grouping ensures similarity analysis captures **structural behavior**, not just size or liquidity effects.



## Core Sectors to Include

### 1. Layer-1 Blockchains (Smart Contract Platforms)

**Examples**
- ETH, SOL, ADA, AVAX, DOT

**Why**
- Backbone of crypto ecosystem  
- Strong macro sentiment drivers

**Selection**
- Top **10–15** by market cap  
- ≥ 6 months of history



### 2. Layer-2 Scaling Solutions

**Examples**
- MATIC, ARB, OP, STRK

**Why**
- Distinct risk/return vs L1s  
- Ethereum-adjacent growth exposure

**Selection**
- Top **5–8** by TVL or market cap



### 3. DeFi (Decentralized Finance)

**Examples**
- UNI, AAVE, MKR, CRV, LDO

**Why**
- Revenue-linked protocols  
- Often decouple during sector rotations

**Selection**
- Top **10–12** by TVL or protocol revenue



### 4. Infrastructure & Oracles

**Examples**
- LINK, GRT, FIL, RNDR

**Why**
- B2B-style demand  
- Less price correlation with L1s

**Selection**
- **5–7** by market cap & usage



### 5. Exchange & CEX Tokens

**Examples**
- BNB, OKB, KCS

**Why**
- Tied to centralized exchange economics  
- Different regulatory risk profile

**Selection**
- **3–5** by exchange trading volume



### 6. Privacy & Alternative Consensus

**Examples**
- XMR, ZEC, LTC

**Why**
- Unique regulatory and adoption drivers

**Selection**
- **3–5** established tokens



### 7. Memecoins & Community-Driven (Optional)

**Examples**
- DOGE, SHIB, PEPE

**Why**
- High retail participation  
- Captures sentiment-driven clusters

**Selection**
- Top **3–5** by market cap (if included)



### 8. Bitcoin & Stablecoins (Anchors)

**Assets**
- BTC  
- USDT, USDC

**Why**
- BTC: market leader, unique dynamics  
- Stablecoins: zero-volatility baseline



## Part 3: Practical Implementation Steps



### Step 1: Data Source Selection

Recommended APIs:
- **CoinGecko API** – market cap, categories
- **CoinMarketCap API** – alternative rankings
- **CryptoCompare API** – historical OHLCV
- **Binance API** – high-quality exchange data

**Recommended setup**
- CoinGecko → filtering & sector tags  
- CryptoCompare → historical price data



### Step 2: Initial Data Pull

For each token:
- `market_cap`
- `24h_volume`
- `exchange_list`
- `price_history (365+ days)`

Derived metrics:
- `avg_daily_volume (30d)`
- `data_completeness (%)`



### Step 3: Apply Filters Sequentially

1. Market cap > $100M → `filtered_list_1`
2. Liquidity criteria → `filtered_list_2`
3. Data continuity → `filtered_list_3`
4. Tier-1 exchange → `filtered_list_4`
5. Manual cleanup:
   - Remove scams
   - Remove most stablecoins (keep USDT/USDC only)



### Step 4: Sector Assignment

- Use CoinGecko categories or manual classification
- Rank tokens **within each sector**
- Select top **N per sector**

**Target universe**
- **80–120 tokens**



### Step 5: Download Historical Data

**Minimum**
- Daily OHLCV, last **12 months**

**Preferred**
- **24 months** (captures full market cycle)

**Frequency**
- Daily (hourly adds complexity without major benefit)



## Final Filtered Universe Summary

| Stage | Token Count | Key Action |
|------|------------|-----------|
| Starting universe | ~14,000 | All listed cryptos |
| Market cap filter | ~500–800 | Remove micro-caps |
| Liquidity filter | ~300–500 | Remove illiquid assets |
| Data quality filter | ~200–300 | Ensure continuity |
| Exchange filter | ~150–200 | Tier-1 exchanges |
| Sector selection | **80–120** | Balanced, diverse universe |



## Key Outcome

Your final universe is:

- ✅ Economically meaningful  
- ✅ Statistically robust  
- ✅ Sectorally diverse  
- ✅ Computationally manageable  
  *(120 tokens → 7,140 pairwise comparisons)*

This universe is **ideal for similarity analysis, clustering, and regime detection**—producing results that are **actionable, interpretable, and reliable**.


