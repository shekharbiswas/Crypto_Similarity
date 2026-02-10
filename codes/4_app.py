import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Crypto Similarity Finder",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🪙 Crypto Similarity Dashboard</p>', unsafe_allow_html=True)
st.markdown("### *Find cryptocurrencies with similar performance patterns*")

# Sidebar
st.sidebar.header("⚙️ Configuration")

# Load data function with caching
@st.cache_data
def load_data():
    # Replace with your actual file path
    df = pd.read_csv('..//outputs//crypto_data.csv')  # Your merged dataframe
    df['date'] = pd.to_datetime(df['date'])
    return df

# Feature engineering
@st.cache_data
def engineer_features(df):
    """Calculate returns, volatility, and other metrics"""
    df = df.sort_values(['symbol', 'date'])
    
    # Daily returns
    df['returns'] = df.groupby('symbol')['price'].pct_change()
    
    # Rolling metrics
    df['volatility_7d'] = df.groupby('symbol')['returns'].transform(
        lambda x: x.rolling(7, min_periods=1).std()
    )
    df['volatility_30d'] = df.groupby('symbol')['returns'].transform(
        lambda x: x.rolling(30, min_periods=1).std()
    )
    df['price_ma_7'] = df.groupby('symbol')['price'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    df['price_ma_30'] = df.groupby('symbol')['price'].transform(
        lambda x: x.rolling(30, min_periods=1).mean()
    )
    df['volume_ma_7'] = df.groupby('symbol')['volume'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    
    return df

# Calculate correlation matrix
@st.cache_data
def calculate_correlation_matrix(df, coins, metric='returns'):
    """Calculate pairwise correlation between selected coins"""
    pivot_df = df[df['symbol'].isin(coins)].pivot(
        index='date', columns='symbol', values=metric
    )
    correlation_matrix = pivot_df.corr()
    return correlation_matrix

# Calculate similarity score
def calculate_similarity_scores(df, reference_coin, top_n=10):
    """Find most similar coins to reference coin based on returns correlation"""
    # Get all coins except reference
    all_coins = df['symbol'].unique()
    coins_to_compare = [c for c in all_coins if c != reference_coin]
    
    # Calculate correlation with reference coin
    similarities = {}
    
    for coin in coins_to_compare:
        try:
            ref_returns = df[df['symbol'] == reference_coin].set_index('date')['returns'].dropna()
            coin_returns = df[df['symbol'] == coin].set_index('date')['returns'].dropna()
            
            # Align dates
            common_dates = ref_returns.index.intersection(coin_returns.index)
            if len(common_dates) > 30:  # At least 30 days of data
                corr = ref_returns[common_dates].corr(coin_returns[common_dates])
                similarities[coin] = corr
        except:
            continue
    
    # Sort and get top N
    similar_coins = pd.Series(similarities).sort_values(ascending=False).head(top_n)
    return similar_coins

# Load data
try:
    df = load_data()
    df = engineer_features(df)
    
    # Sidebar filters
    st.sidebar.subheader("📊 Data Filters")
    
    # Date range
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(max_date - timedelta(days=90), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Market cap filter
    market_caps = ['All'] + sorted(df['market_cap_category'].dropna().unique().tolist())
    selected_cap = st.sidebar.selectbox("Market Cap Category", market_caps)
    
    # Filter data
    mask = (df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))
    filtered_df = df[mask].copy()
    
    if selected_cap != 'All':
        filtered_df = filtered_df[filtered_df['market_cap_category'] == selected_cap]
    
    # Get available coins
    available_coins = sorted(filtered_df['symbol'].unique())
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Coins", len(available_coins))
    with col2:
        st.metric("Date Range", f"{(date_range[1] - date_range[0]).days} days")
    with col3:
        avg_volatility = filtered_df.groupby('symbol')['volatility_30d'].mean().mean()
        st.metric("Avg Volatility", f"{avg_volatility:.2%}")
    with col4:
        total_volume = filtered_df.groupby('symbol')['volume'].sum().sum() / 1e9
        st.metric("Total Volume", f"${total_volume:.1f}B")
    
    st.markdown("---")
    
    # Tab navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Similarity Finder", 
        "📈 Price Comparison", 
        "🔥 Correlation Heatmap",
        "🌳 Clustering",
        "📊 Market Overview"
    ])
    
    # TAB 1: Similarity Finder
    with tab1:
        st.header("🎯 Find Similar Cryptocurrencies")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Select Reference Coin")
            reference_coin = st.selectbox(
                "Choose a cryptocurrency:",
                available_coins,
                index=0
            )
            
            top_n = st.slider("Number of similar coins to show:", 5, 20, 10)
            
            if st.button("🔍 Find Similar Coins", type="primary"):
                with st.spinner("Calculating similarities..."):
                    similar_coins = calculate_similarity_scores(filtered_df, reference_coin, top_n)
                    
                    st.success(f"Found {len(similar_coins)} similar coins!")
                    
                    # Display results
                    st.subheader(f"Most Similar to **{reference_coin}**")
                    
                    results_df = pd.DataFrame({
                        'Coin': similar_coins.index,
                        'Similarity Score': similar_coins.values,
                        'Similarity %': (similar_coins.values * 100).round(2)
                    }).reset_index(drop=True)
                    results_df.index = results_df.index + 1
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Store in session state for other tabs
                    st.session_state['similar_coins'] = similar_coins.index.tolist()
                    st.session_state['reference_coin'] = reference_coin
        
        with col2:
            if 'similar_coins' in st.session_state:
                st.subheader("Similarity Score Visualization")
                
                # Bar chart
                fig = px.bar(
                    results_df,
                    x='Coin',
                    y='Similarity %',
                    color='Similarity %',
                    color_continuous_scale='Viridis',
                    title=f'Top {top_n} Coins Similar to {reference_coin}'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Price comparison
                st.subheader("Price Movement Comparison")
                coins_to_plot = [reference_coin] + st.session_state['similar_coins'][:5]
                
                fig = go.Figure()
                for coin in coins_to_plot:
                    coin_data = filtered_df[filtered_df['symbol'] == coin].sort_values('date')
                    # Normalize to 100
                    normalized_price = (coin_data['price'] / coin_data['price'].iloc[0]) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=coin_data['date'],
                        y=normalized_price,
                        mode='lines',
                        name=coin,
                        line=dict(width=3 if coin == reference_coin else 1.5)
                    ))
                
                fig.update_layout(
                    title='Normalized Price Trends (Base=100)',
                    xaxis_title='Date',
                    yaxis_title='Normalized Price',
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: Price Comparison
    with tab2:
        st.header("📈 Multi-Coin Price Comparison")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            selected_coins = st.multiselect(
                "Select coins to compare:",
                available_coins,
                default=available_coins[:5] if len(available_coins) >= 5 else available_coins
            )
            
            normalize = st.checkbox("Normalize prices (Base=100)", value=True)
            show_volume = st.checkbox("Show volume", value=False)
        
        with col2:
            if selected_coins:
                if show_volume:
                    fig = make_subplots(
                        rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3],
                        subplot_titles=('Price', 'Volume')
                    )
                    
                    for coin in selected_coins:
                        coin_data = filtered_df[filtered_df['symbol'] == coin].sort_values('date')
                        
                        if normalize:
                            price_data = (coin_data['price'] / coin_data['price'].iloc[0]) * 100
                        else:
                            price_data = coin_data['price']
                        
                        fig.add_trace(
                            go.Scatter(x=coin_data['date'], y=price_data, name=coin, mode='lines'),
                            row=1, col=1
                        )
                        
                        fig.add_trace(
                            go.Bar(x=coin_data['date'], y=coin_data['volume'], name=coin, showlegend=False),
                            row=2, col=1
                        )
                    
                    fig.update_yaxes(title_text="Price" if not normalize else "Normalized Price", row=1, col=1)
                    fig.update_yaxes(title_text="Volume", row=2, col=1)
                    fig.update_layout(height=600, hovermode='x unified')
                    
                else:
                    fig = go.Figure()
                    
                    for coin in selected_coins:
                        coin_data = filtered_df[filtered_df['symbol'] == coin].sort_values('date')
                        
                        if normalize:
                            price_data = (coin_data['price'] / coin_data['price'].iloc[0]) * 100
                        else:
                            price_data = coin_data['price']
                        
                        fig.add_trace(go.Scatter(
                            x=coin_data['date'],
                            y=price_data,
                            mode='lines',
                            name=coin
                        ))
                    
                    fig.update_layout(
                        title='Price Comparison',
                        xaxis_title='Date',
                        yaxis_title='Price' if not normalize else 'Normalized Price (Base=100)',
                        hovermode='x unified',
                        height=500
                    )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Returns distribution
                st.subheader("Returns Distribution")
                
                returns_data = []
                for coin in selected_coins:
                    coin_returns = filtered_df[filtered_df['symbol'] == coin]['returns'].dropna()
                    returns_data.extend([(coin, r) for r in coin_returns])
                
                returns_df = pd.DataFrame(returns_data, columns=['Coin', 'Returns'])
                
                fig = px.box(
                    returns_df,
                    x='Coin',
                    y='Returns',
                    color='Coin',
                    title='Daily Returns Distribution'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: Correlation Heatmap
    with tab3:
        st.header("🔥 Correlation Heatmap")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Settings")
            
            # Coin selection for heatmap
            num_coins = st.slider("Number of coins to analyze:", 10, 50, 20)
            
            # Get top coins by volume
            top_coins_by_volume = (
                filtered_df.groupby('symbol')['volume']
                .sum()
                .sort_values(ascending=False)
                .head(num_coins)
                .index.tolist()
            )
            
            heatmap_coins = st.multiselect(
                "Or select specific coins:",
                available_coins,
                default=top_coins_by_volume[:num_coins]
            )
            
            if not heatmap_coins:
                heatmap_coins = top_coins_by_volume
            
            metric_for_corr = st.selectbox(
                "Correlation metric:",
                ['returns', 'price', 'volume'],
                index=0
            )
        
        with col2:
            if len(heatmap_coins) >= 2:
                with st.spinner("Calculating correlations..."):
                    corr_matrix = calculate_correlation_matrix(filtered_df, heatmap_coins, metric_for_corr)
                    
                    # Plotly heatmap
                    fig = px.imshow(
                        corr_matrix,
                        text_auto='.2f',
                        aspect='auto',
                        color_continuous_scale='RdBu_r',
                        zmin=-1,
                        zmax=1,
                        title=f'{metric_for_corr.capitalize()} Correlation Matrix'
                    )
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Highly correlated pairs
                    st.subheader("🔗 Highly Correlated Pairs (>0.7)")
                    
                    corr_pairs = []
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            corr_val = corr_matrix.iloc[i, j]
                            if corr_val > 0.7:
                                corr_pairs.append({
                                    'Coin 1': corr_matrix.columns[i],
                                    'Coin 2': corr_matrix.columns[j],
                                    'Correlation': corr_val
                                })
                    
                    if corr_pairs:
                        pairs_df = pd.DataFrame(corr_pairs).sort_values('Correlation', ascending=False)
                        st.dataframe(pairs_df, use_container_width=True)
                        
                        st.info(f"💡 **Insight:** Found {len(pairs_df)} highly correlated pairs. "
                               "Consider these as similar assets to avoid redundant holdings!")
                    else:
                        st.warning("No highly correlated pairs found (>0.7)")
            else:
                st.warning("Please select at least 2 coins for correlation analysis")
    
    # TAB 4: Clustering
    with tab4:
        st.header("🌳 Hierarchical Clustering")
        st.markdown("*Groups coins with similar behavior patterns*")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            cluster_coins_count = st.slider("Number of coins to cluster:", 10, 50, 25)
            
            # Get top coins
            cluster_coins = (
                filtered_df.groupby('symbol')['volume']
                .sum()
                .sort_values(ascending=False)
                .head(cluster_coins_count)
                .index.tolist()
            )
            
            linkage_method = st.selectbox(
                "Linkage method:",
                ['ward', 'complete', 'average', 'single'],
                index=0
            )
        
        with col2:
            if len(cluster_coins) >= 3:
                with st.spinner("Performing clustering..."):
                    # Calculate correlation matrix
                    corr_matrix = calculate_correlation_matrix(filtered_df, cluster_coins, 'returns')
                    
                    # Convert correlation to distance
                    distance_matrix = 1 - corr_matrix.abs()
                    
                    # Hierarchical clustering
                    condensed_dist = squareform(distance_matrix)
                    linkage_matrix = linkage(condensed_dist, method=linkage_method)
                    
                    # Plot dendrogram
                    fig, ax = plt.subplots(figsize=(12, 6))
                    dendrogram(
                        linkage_matrix,
                        labels=corr_matrix.columns,
                        ax=ax,
                        leaf_rotation=90,
                        leaf_font_size=10
                    )
                    ax.set_title('Hierarchical Clustering Dendrogram', fontsize=14, fontweight='bold')
                    ax.set_xlabel('Cryptocurrency', fontsize=12)
                    ax.set_ylabel('Distance', fontsize=12)
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    st.info("💡 **How to read:** Coins that merge at lower heights are more similar. "
                           "Use this to identify clusters of similar-behaving assets!")
    
    # TAB 5: Market Overview
    with tab5:
        st.header("📊 Market Overview")
        
        # Market cap distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Cap Distribution")
            
            latest_data = filtered_df.groupby('symbol').last().reset_index()
            latest_data['market_cap'] = latest_data['price'] * latest_data['circulatingSupply']
            
            fig = px.pie(
                latest_data,
                names='market_cap_category',
                title='Distribution by Market Cap Category',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Exchange Distribution")
            
            exchange_counts = latest_data['exchange'].value_counts().head(10)
            
            fig = px.bar(
                x=exchange_counts.index,
                y=exchange_counts.values,
                title='Top 10 Exchanges by Number of Coins',
                labels={'x': 'Exchange', 'y': 'Number of Coins'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Volatility analysis
        st.subheader("📉 Volatility Analysis")
        
        volatility_data = filtered_df.groupby('symbol').agg({
            'volatility_30d': 'mean',
            'price': 'last',
            'volume': 'sum'
        }).reset_index()
        volatility_data = volatility_data.dropna()
        
        fig = px.scatter(
            volatility_data,
            x='volume',
            y='volatility_30d',
            size='price',
            hover_data=['symbol'],
            title='Volatility vs Volume',
            labels={'volatility_30d': '30-Day Volatility', 'volume': 'Total Volume'},
            log_x=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 Top Gainers")
            
            latest_returns = (
                filtered_df.groupby('symbol')
                .apply(lambda x: ((x['price'].iloc[-1] / x['price'].iloc[0]) - 1) * 100)
                .sort_values(ascending=False)
                .head(10)
            )
            
            st.dataframe(
                pd.DataFrame({
                    'Coin': latest_returns.index,
                    'Gain %': latest_returns.values.round(2)
                }),
                use_container_width=True
            )
        
        with col2:
            st.subheader("📉 Top Losers")
            
            losers = (
                filtered_df.groupby('symbol')
                .apply(lambda x: ((x['price'].iloc[-1] / x['price'].iloc[0]) - 1) * 100)
                .sort_values(ascending=True)
                .head(10)
            )
            
            st.dataframe(
                pd.DataFrame({
                    'Coin': losers.index,
                    'Loss %': losers.values.round(2)
                }),
                use_container_width=True
            )

except FileNotFoundError:
    st.error("❌ **Error:** Could not find 'crypto_data.csv'. Please make sure the file exists in the same directory.")
    st.info("💡 **Tip:** Update the file path in the `load_data()` function (line 54)")
except Exception as e:
    st.error(f"❌ **Error:** {str(e)}")
    st.info("Check your data format and try again.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🪙 Crypto Similarity Dashboard | Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True
)