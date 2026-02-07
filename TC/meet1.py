# Pseudo-code structure for FMP data collection

# Step 1: Get universe of all cryptos
all_cryptos = fmp.get_crypto_list()  # Returns ~14k tokens

# Step 2: For each token, collect:
for token in all_cryptos:
    # Point 1: Core market data
    ohlcv = fmp.get_historical_prices(token, period='2y')
    
    # Point 2: Liquidity metrics
    volume_stats = calculate_volume_metrics(ohlcv)
    data_quality = check_data_completeness(ohlcv)
    
    # Point 3: Metadata
    sector = fmp.get_crypto_profile(token)['sector']
    blockchain = fmp.get_crypto_profile(token)['platform']
    
    # Point 4: Fundamentals (if available)
    fundamentals = fmp.get_crypto_fundamentals(token)
    
    # Apply your filters from the document
    if passes_filters(token, volume_stats, data_quality):
        final_universe.append(token)

# Step 3: Compute similarity features (Point 5)
for token in final_universe:
    compute_statistical_features(token)
