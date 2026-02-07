#### 1. Core Market & Trading Data

**Collect**
- Daily OHLCV for last 24 months
- Market capitalization (daily snapshots)
- Circulating supply & total supply
- 24h trading volume (all exchanges)
- Exchange count + dominant exchange by volume

**Purpose**
Forms the base layer for price similarity, volatility modeling, and liquidity analysis.


#### 2. Liquidity & Data Quality Metrics

**Collect**
- Avg daily volume (7d / 30d / 90d rolling)
- Bid–ask spread (if API available)
- Data completeness (% valid days, 12 months)
- Zero-volume day count
- Price change distribution
- Last traded timestamp

**Purpose**
Filters illiquid or unreliable assets and prevents distorted similarity signals.


#### 3. Sector & Classification Metadata

**Collect**
- Sector tags (L1, DeFi, Oracle, Meme, etc.)
- Token type (utility / governance / stablecoin / wrapped)
- Blockchain/platform
- Launch date / asset age
- Status flags (active / deprecated / migrated)

**Purpose**
Enables sector-aware clustering and interpretability of model results.


#### 4. On-Chain & Fundamental Metrics (Optional)

**Collect**
- Active addresses
- Transaction count & volume
- TVL (for DeFi protocols)
- Staking or locked supply ratio
- Developer activity (e.g., GitHub commits)
- Token unlock schedule

**Purpose**
Captures behavioral and usage similarity beyond price correlation.

#### 5. Derived Statistical Features

**Compute after collection**
- 30d / 90d / 180d rolling volatility
- Beta vs BTC & ETH
- Sharpe ratio
- Max drawdown
- Pairwise correlation matrix
- VWAP divergence

**Purpose**
Transforms raw data into model-ready statistical features.

#### Goals

Create a clean, comparable dataset that supports:
- similarity modeling
- clustering
- liquidity filtering
- risk profiling
- sector analysis
