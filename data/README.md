# Cryptocurrency Data Collection System

Complete Python solution for collecting comprehensive cryptocurrency market data from Financial Modeling Prep API.

## What this does

Collects and processes cryptocurrency data for:
- **Price similarity analysis**
- **Volatility modeling**
- **Liquidity analysis**
- **Sector clustering**
- **Risk profiling**

## Files Included

### 1. `crypto_data_fetcher.py` - **Basic Collector**
Simple, fast collection of current market snapshots.

**Features:**
- Current price, volume, market cap
- 50-day and 200-day moving averages
- Year high/low
- Basic derived metrics
- Single CSV output

**Best for:** Quick market overview, current state analysis

### 2. `advanced_crypto_collector.py` 
Comprehensive data collection with historical OHLCV and advanced metrics.

**Features:**
- 24-month historical OHLCV data
- Liquidity metrics (7d/30d/90d volumes)
- Data quality metrics (completeness, zero-volume days)
- Volatility calculations (30d/90d/180d)
- Beta vs BTC & ETH
- Sharpe ratio
- Max drawdown
- Market cap filtering
- Two CSV outputs (snapshot + historical)

**Best for:** Statistical analysis, modeling, research

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run basic collector
python crypto_data_fetcher.py

# Run advanced collector (recommended)
python advanced_crypto_collector.py
```

## ⚙️ Configuration

### Basic Collector (`crypto_data_fetcher.py`)

Edit the `main()` function:

```python
# Collect sample (for testing)
df = fetcher.fetch_all_crypto_data(sample_size=100, delay=0.2)

# Collect ALL cryptocurrencies
df = fetcher.fetch_all_crypto_data(sample_size=None, delay=0.2)
```

### Advanced Collector (`advanced_crypto_collector.py`)

Edit the `CONFIG` dictionary in `main()`:

```python
CONFIG = {
    'top_n': 500,              # Top N by market cap (None = all)
    'include_historical': True, # Fetch OHLCV data
    'historical_months': 24,    # Months of history
    'min_market_cap': 1e6      # Minimum $1M market cap
}
```

**Examples:**

```python
# Top 100 cryptos, 12 months history
CONFIG = {
    'top_n': 100,
    'include_historical': True,
    'historical_months': 12,
    'min_market_cap': 10e6  # $10M minimum
}

# All cryptos above $50M market cap, no historical
CONFIG = {
    'top_n': None,
    'include_historical': False,
    'historical_months': 24,
    'min_market_cap': 50e6
}

# Top 1000, full 24-month history
CONFIG = {
    'top_n': 1000,
    'include_historical': True,
    'historical_months': 24,
    'min_market_cap': 1e6
}
```

## Data Output

### Basic Collector Output

**File:** `cryptocurrency_market_data.csv`

**Columns:**
- Basic info: `symbol`, `name`, `exchange`, `icoDate`
- Supply: `circulatingSupply`, `totalSupply`
- Price: `price`, `open`, `previousClose`
- Range: `dayLow`, `dayHigh`, `yearLow`, `yearHigh`
- Volume: `volume`
- Market: `marketCap`, `priceAvg50`, `priceAvg200`
- Derived: `daily_range_pct`, `ytd_gain_pct`, `distance_from_50ma_pct`, etc.

### Advanced Collector Output

**Two files:**

1. **`crypto_snapshot_TIMESTAMP.csv`** - Current market state
   - All basic columns PLUS:
   - **Liquidity metrics:** `avg_volume_7d`, `avg_volume_30d`, `avg_volume_90d`
   - **Data quality:** `data_days_available`, `data_completeness_pct`, `zero_volume_days`
   - **Volatility:** `volatility_30d`, `volatility_90d`, `volatility_180d`
   - **Performance:** `max_drawdown_pct`, `sharpe_ratio`
   - **Beta:** `beta_vs_btc`, `beta_vs_eth`
   - **Categories:** `mcap_category`, `asset_age_days`

2. **`crypto_historical_ohlcv_TIMESTAMP.csv`** - Daily OHLCV data
   - `symbol`, `date`
   - `open`, `high`, `low`, `close`
   - `volume`

## Use Cases

### 1. Price Similarity Analysis
```python
# Use snapshot data
df = pd.read_csv('crypto_snapshot_*.csv')

# Calculate correlation matrix
price_features = ['volatility_30d', 'beta_vs_btc', 'sharpe_ratio']
correlation_matrix = df[price_features].corr()
```

### 2. Liquidity Filtering
```python
# Filter high-quality assets
quality_df = df[
    (df['data_completeness_pct'] > 80) &
    (df['zero_volume_pct'] < 10) &
    (df['avg_volume_30d'] > 1e6)
]
```

### 3. Volatility Clustering
```python
# Group by volatility
from sklearn.cluster import KMeans

features = df[['volatility_90d', 'max_drawdown_pct']].dropna()
kmeans = KMeans(n_clusters=5)
df['volatility_cluster'] = kmeans.fit_predict(features)
```

### 4. Sector Analysis
```python
# Analyze by market cap category
sector_stats = df.groupby('mcap_category').agg({
    'volatility_30d': 'mean',
    'sharpe_ratio': 'mean',
    'beta_vs_btc': 'mean'
})
```

## 🎯 Mapped to Your Objectives

| Objective | File | Columns/Features |
|-----------|------|------------------|
| **Daily OHLCV (24 months)** | `crypto_historical_ohlcv_*.csv` | `date`, `open`, `high`, `low`, `close`, `volume` |
| **Market cap snapshots** | `crypto_snapshot_*.csv` | `marketCap` |
| **Supply data** | `crypto_snapshot_*.csv` | `circulatingSupply`, `totalSupply` |
| **24h volume** | `crypto_snapshot_*.csv` | `volume` |
| **Avg volumes (7d/30d/90d)** | `crypto_snapshot_*.csv` | `avg_volume_7d`, `avg_volume_30d`, `avg_volume_90d` |
| **Data completeness** | `crypto_snapshot_*.csv` | `data_completeness_pct`, `zero_volume_days` |
| **Volatility (30/90/180d)** | `crypto_snapshot_*.csv` | `volatility_30d`, `volatility_90d`, `volatility_180d` |
| **Beta vs BTC & ETH** | `crypto_snapshot_*.csv` | `beta_vs_btc`, `beta_vs_eth` |
| **Sharpe ratio** | `crypto_snapshot_*.csv` | `sharpe_ratio` |
| **Max drawdown** | `crypto_snapshot_*.csv` | `max_drawdown_pct` |
| **Exchange info** | `crypto_snapshot_*.csv` | `exchange` |
| **Launch date/age** | `crypto_snapshot_*.csv` | `icoDate`, `asset_age_days` |

## ⚡ Performance & Rate Limiting

- **Rate limit:** 0.15-0.2 seconds between requests
- **Estimated time:**
  - 100 cryptos (no historical): ~30 seconds
  - 100 cryptos (with historical): ~3 minutes
  - 500 cryptos (with historical): ~15 minutes
  - 1000 cryptos (with historical): ~30 minutes

## 🔧 Troubleshooting

### API Rate Limits
If you hit rate limits, increase the `delay` parameter:
```python
time.sleep(0.3)  # Instead of 0.2
```

### Memory Issues
For large datasets, process in batches:
```python
CONFIG = {'top_n': 200}  # Instead of all
```

### Missing Historical Data
Some newer/smaller cryptos may not have 24 months of data. The script handles this gracefully and reports data completeness.

## Example Workflow

```python
import pandas as pd
import numpy as np

# 1. Load data
snapshot = pd.read_csv('crypto_snapshot_*.csv')
historical = pd.read_csv('crypto_historical_ohlcv_*.csv')

# 2. Filter quality assets
quality = snapshot[
    (snapshot['data_completeness_pct'] > 70) &
    (snapshot['marketCap'] > 10e6)
]

# 3. Calculate additional metrics
quality['volume_stability'] = quality['avg_volume_7d'] / quality['avg_volume_90d']

# 4. Cluster by similarity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

features = ['volatility_90d', 'beta_vs_btc', 'sharpe_ratio', 'max_drawdown_pct']
X = quality[features].dropna()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=6, random_state=42)
quality['cluster'] = kmeans.fit_predict(X_scaled)

# 5. Analyze clusters
cluster_profile = quality.groupby('cluster')[features].mean()
print(cluster_profile)
```

## Next Steps

After collecting data:

1. **Data cleaning:** Handle missing values, outliers
2. **Feature engineering:** Create custom metrics
3. **Similarity matrix:** Calculate pairwise correlations
4. **Clustering:** Group similar assets
5. **Backtesting:** Validate on historical data
6. **Modeling:** Build predictive models

## Support

- **API Documentation:** https://site.financialmodelingprep.com/developer/docs
- **Rate Limits:** Check your plan limits
- **Historical Data:** Some endpoints may require higher-tier plans

## 📄 License

Free to use with your Financial Modeling Prep API key.


**Version:** 1.0  
**Last Updated:** February 2026