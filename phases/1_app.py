"""
╔══════════════════════════════════════════════════════════════╗
║   CRYPTO INTELLIGENCE DASHBOARD  —  Streamlit Edition        ║
║   Run:  streamlit run app.py                                 ║
║   Data: crypto_data.csv  (same folder as this file)         ║
╚══════════════════════════════════════════════════════════════╝
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import polars as pl
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats as scipy_stats

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title  = "Crypto Intelligence",
    page_icon   = "◈",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

# ══════════════════════════════════════════════════════════════
#  GLOBAL STYLES  (injected CSS)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&family=Open+Sans:wght@400;600;700;800&display=swap');

:root {
    --bg:       #0a0e1a;
    --grid:     #0f1629;
    --card:     #111827;
    --border:   #1e2d45;
    --accent:   #00f5d4;
    --accent2:  #f72585;
    --gold:     #ffd60a;
    --text:     #e2e8f0;
    --muted:    #64748b;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="stSidebar"] {
    background: #0d1220 !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
header { visibility: hidden; }

[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    gap: 12px !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    flex: 1 1 0% !important;
    min-width: 0 !important;
    width: 0 !important;
}
[data-testid="stColumn"] [data-testid="stMetric"] {
    width: 100% !important;
    height: 100% !important;
    box-sizing: border-box !important;
}

@keyframes cardGlow {
    0%   { box-shadow: 0 0 6px rgba(0,245,212,0.10), 0 0 0px rgba(0,245,212,0.05); border-color: #1e2d45; }
    50%  { box-shadow: 0 0 18px rgba(0,245,212,0.35), 0 0 40px rgba(0,245,212,0.10); border-color: rgba(0,245,212,0.45); }
    100% { box-shadow: 0 0 6px rgba(0,245,212,0.10), 0 0 0px rgba(0,245,212,0.05); border-color: #1e2d45; }
}

@keyframes accentPulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.7; }
}

[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    animation: cardGlow 4s ease-in-out infinite;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 28px rgba(0,245,212,0.5) !important;
    border-color: var(--accent) !important;
    animation: none;
}

[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] { animation-delay: 0s; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] { animation-delay: 0.7s; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] { animation-delay: 1.4s; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] { animation-delay: 2.1s; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] { animation-delay: 2.8s; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(6) [data-testid="stMetric"] { animation-delay: 3.5s; }

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
[data-testid="stMetricDelta"] { font-size: 11px !important; }

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div[style*="color:#00f5d4"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div[style*="color: #00f5d4"] {
    animation: accentPulse 3s ease-in-out infinite;
}

[data-testid="stSelectbox"] > div > div,
[data-testid="stRadio"] { color: var(--text) !important; }

[data-testid="stTabs"] button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    color: var(--muted) !important;
    transition: color 0.2s ease;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    text-shadow: 0 0 10px rgba(0,245,212,0.6);
}

[data-testid="stExpander"] summary {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--accent) !important;
}

hr { border-color: var(--border) !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PALETTE & HELPERS
# ══════════════════════════════════════════════════════════════
BG      = "#0a0e1a"
GRID    = "#0f1629"
CARD    = "#111827"
ACCENT  = "#00f5d4"
ACCENT2 = "#f72585"
GOLD    = "#ffd60a"
TEXT    = "#e2e8f0"
MUTED   = "#4a5568"

TIER_COLORS = {
    "mega":  "#f72585",
    "large": "#7209b7",
    "mid":   "#3a0ca3",
    "small": "#4361ee",
    "micro": "#4cc9f0",
}

AXIS_BASE = dict(
    gridcolor     = "#1a2540",
    zerolinecolor = "#1a2540",
    title_font    = dict(color=MUTED, family="JetBrains Mono"),
)
AXIS = dict(
    **AXIS_BASE,
    tickfont = dict(color=MUTED, family="JetBrains Mono"),
)

def axis_tf(color=None, family="JetBrains Mono", size=None, **extra):
    """Return an axis dict with a custom tickfont, safe from duplicate-key errors."""
    tf = dict(color=color or MUTED, family=family)
    if size is not None:
        tf["size"] = size
    return {**AXIS_BASE, "tickfont": tf, **extra}

BASE_LAYOUT = dict(
    paper_bgcolor = BG,
    plot_bgcolor  = GRID,
    font          = dict(family="JetBrains Mono, monospace", color=TEXT, size=12),
    margin        = dict(t=60, b=40, l=50, r=30),
    hoverlabel    = dict(
        bgcolor   = "#1a2035",
        font_size = 13,
        font_family = "JetBrains Mono",
    ),
)

def title_cfg(text, size=17):
    return dict(
        text = text, x = 0.01,
        font = dict(size=size, color=ACCENT, family="JetBrains Mono"),
    )

# ══════════════════════════════════════════════════════════════
#  DATA LOADING  (cached)
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Loading crypto data...")
def load_data(path: str = "crypto_data.csv"):
    df = (
        pl.read_csv(path, try_parse_dates=True)
        .with_columns([
            pl.col("date").cast(pl.Date),
            pl.col("close").cast(pl.Float64),
            pl.col("open").cast(pl.Float64),
            pl.col("high").cast(pl.Float64),
            pl.col("low").cast(pl.Float64),
            pl.col("volume_usd").cast(pl.Float64),
            pl.col("market_cap_usd").cast(pl.Float64),
            pl.col("change_24h_pct").cast(pl.Float64),
            pl.col("is_stablecoin").cast(pl.Boolean),
        ])
        .filter(pl.col("is_stablecoin") == False)
        .filter(pl.col("date") >= pl.date(2020, 1, 1))
        .sort(["coin_id", "date"])
    )
    df = df.with_columns([
        (pl.col("close") / pl.col("close").shift(1).over("coin_id"))
        .log().alias("log_ret")
    ])
    return df

@st.cache_data(show_spinner="Computing summary stats...")
def build_summary(_df):
    summary = (
        _df
        .group_by(["coin_id", "symbol", "name", "cap_tier"])
        .agg([
            pl.col("log_ret").mean().alias("mean_daily_ret"),
            pl.col("log_ret").std().alias("volatility"),
            pl.col("log_ret").sum().alias("total_log_ret"),
            pl.col("market_cap_usd").last().alias("market_cap"),
            pl.col("volume_usd").mean().alias("avg_vol"),
            pl.col("close").last().alias("last_price"),
            pl.col("ath").first().alias("ath"),
            pl.col("atl").first().alias("atl"),
        ])
        .with_columns([
            (pl.col("mean_daily_ret") / pl.col("volatility")).alias("sharpe_proxy"),
            # FIX: fill_null(0.0) prevents null total_log_ret from silently nulling total_ret_pct
            (
                (pl.col("total_log_ret").fill_null(0.0).exp() - 1) * 100
            ).alias("total_ret_pct"),
        ])
        .sort("market_cap", descending=True)
    )

    latest = _df["date"].max()
    PERIODS = {"1M":30,"3M":90,"6M":180,"1Y":365,"3Y":365*3,"4Y":365*4}

    coin_first = (
        _df.group_by("coin_id")
        .agg(pl.col("date").min().alias("first_date"))
    )

    for label, days in PERIODS.items():
        cutoff = latest - pl.duration(days=days)
        eligible = (
            coin_first
            .filter(pl.col("first_date") <= cutoff)
            .select("coin_id")
        )
        start = (
            _df.join(eligible, on="coin_id")
            .filter(pl.col("date") >= cutoff)
            .group_by("coin_id")
            .agg(pl.col("close").first().alias("sc"))
        )
        end = (
            _df.group_by("coin_id")
            .agg(pl.col("close").last().alias("ec"))
        )
        ret = (
            start.join(end, on="coin_id")
            .with_columns(
                ((pl.col("ec") - pl.col("sc")) / pl.col("sc") * 100)
                .alias(f"ret_{label}")
            )
            .select(["coin_id", f"ret_{label}"])
        )
        summary = summary.join(ret, on="coin_id", how="left")

    return summary.to_pandas()

# ══════════════════════════════════════════════════════════════
#  PHASE 2: SIMILARITY ENGINE HELPERS
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Building return matrix...")
def build_return_matrix(_df, window_days: int):
    """Pivot log_ret into wide DataFrame: rows=date, cols=coin_id."""
    pdf = _df.to_pandas()
    pdf["date"] = pd.to_datetime(pdf["date"])
    latest = pdf["date"].max()
    cutoff = latest - pd.Timedelta(days=window_days)
    pdf = pdf[pdf["date"] >= cutoff]

    pivot = (
        pdf.pivot_table(index="date", columns="coin_id", values="log_ret")
    )
    # Keep only coins with at least 80% data coverage in window
    min_obs = int(0.8 * len(pivot))
    pivot = pivot.dropna(thresh=min_obs, axis=1)
    return pivot


def compute_similarity(pivot: pd.DataFrame, anchor_id: str, top_n: int = 10):
    """
    Pearson correlation of anchor vs all others on shared non-NaN dates.
    Returns DataFrame: coin_id, correlation, p_value, n_obs, pct_same_dir
    """
    if anchor_id not in pivot.columns:
        return pd.DataFrame()

    anchor = pivot[anchor_id].dropna()
    results = []

    for coin in pivot.columns:
        if coin == anchor_id:
            continue
        other = pivot[coin].dropna()
        common = anchor.index.intersection(other.index)
        if len(common) < 30:
            continue
        a = anchor.loc[common].values
        o = other.loc[common].values
        r, p = scipy_stats.pearsonr(a, o)
        pct_dir = np.mean(np.sign(a) == np.sign(o)) * 100
        results.append({
            "coin_id": coin,
            "correlation": r,
            "p_value": p,
            "n_obs": len(common),
            "pct_same_dir": pct_dir,
        })

    if not results:
        return pd.DataFrame()

    res_df = (
        pd.DataFrame(results)
        .sort_values("correlation", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    res_df.index += 1
    return res_df


def get_coin_meta(summary_df: pd.DataFrame, coin_ids: list) -> dict:
    """Map coin_id → {symbol, name, cap_tier}."""
    sub = summary_df[summary_df["coin_id"].isin(coin_ids)]
    return {
        row["coin_id"]: {
            "symbol":   row["symbol"],
            "name":     row["name"],
            "cap_tier": row["cap_tier"],
        }
        for _, row in sub.iterrows()
    }


def rebase_prices(pivot_close: pd.DataFrame, coin_ids: list) -> pd.DataFrame:
    """Rebase each coin's close price to 100 at the start of the window."""
    # Only keep coin_ids that exist in the pivot
    valid_ids = [c for c in coin_ids if c in pivot_close.columns]
    if not valid_ids:
        return pd.DataFrame()
    sub = pivot_close[valid_ids].dropna(how="all")
    rebased = sub.div(sub.bfill().iloc[0]) * 100
    return rebased


def seasonal_monthly_returns(df_pd: pd.DataFrame, coin_id: str) -> pd.DataFrame:
    """
    Build month × year matrix of average monthly returns for a coin.
    Returns a pivot with months as rows (1-12) and years as columns.
    """
    sub = df_pd[df_pd["coin_id"] == coin_id].copy()
    sub["date"] = pd.to_datetime(sub["date"])
    sub["year"]  = sub["date"].dt.year
    sub["month"] = sub["date"].dt.month

    monthly = (
        sub.groupby(["year", "month"])["log_ret"]
        .sum()
        .reset_index()
    )
    monthly["ret_pct"] = (np.exp(monthly["log_ret"]) - 1) * 100

    pivot = monthly.pivot(index="month", columns="year", values="ret_pct")
    pivot.index = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    return pivot


# ══════════════════════════════════════════════════════════════
#  LOAD
# ══════════════════════════════════════════════════════════════
try:
    df      = load_data("crypto_data.csv")
    s       = build_summary(df)
except FileNotFoundError:
    st.error("❌  `crypto_data.csv` not found — place it in the same folder as app.py")
    st.stop()

TIER_ORDER      = ["mega","large","mid","small","micro"]
available_tiers = [t for t in TIER_ORDER if t in s["cap_tier"].values]
PERIOD_COLS     = {"1M":"ret_1M","3M":"ret_3M","6M":"ret_6M",
                   "1Y":"ret_1Y","3Y":"ret_3Y","4Y":"ret_4Y",
                   "All":"total_ret_pct"}   # total_ret_pct exists for every coin

# Pre-compute close pivot (needed by Phase 2 rebase chart)
@st.cache_data(show_spinner="Building close-price matrix...")
def build_close_matrix(_df):
    pdf = _df.to_pandas()
    pdf["date"] = pd.to_datetime(pdf["date"])
    return pdf.pivot_table(index="date", columns="coin_id", values="close")

close_pivot = build_close_matrix(df)
df_pd = df.to_pandas()   # pandas version used in several phase-2 helpers

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<div style='font-family:\"Open Sans\",sans-serif;font-size:22px;"
        "font-weight:800;color:#00f5d4;margin-bottom:4px'>◈ CRYPTO</div>"
        "<div style='font-family:\"Open Sans\",sans-serif;font-size:22px;"
        "font-weight:800;color:#e2e8f0;margin-bottom:20px'>INTELLIGENCE</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:11px;color:{MUTED};margin-bottom:24px'>"
        f"{df['coin_id'].n_unique()} coins  ·  "
        f"{df['date'].min()} → {df['date'].max()}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:{MUTED};text-transform:uppercase;"
        f"letter-spacing:1px;margin-bottom:8px'>Return Period</div>",
        unsafe_allow_html=True,
    )
    period_sel = st.radio(
        label     = "period",
        options   = list(PERIOD_COLS.keys()),
        index     = 3,
        horizontal= True,
        label_visibility = "collapsed",
    )
    period_col = PERIOD_COLS[period_sel]

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:{MUTED};text-transform:uppercase;"
        f"letter-spacing:1px;margin-bottom:8px'>Cap Tiers</div>",
        unsafe_allow_html=True,
    )
    selected_tiers = []
    for t in available_tiers:
        chk = st.checkbox(label=t.upper(), value=True, key=f"tier_{t}")
        if chk:
            selected_tiers.append(t)

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:11px;color:{MUTED};text-transform:uppercase;"
        f"letter-spacing:1px;margin-bottom:8px'>Volatility Clip</div>",
        unsafe_allow_html=True,
    )
    vol_clip = st.slider(
        label="vol", min_value=0.05, max_value=0.50,
        value=0.25, step=0.01, label_visibility="collapsed",
    )
    ret_clip_max = st.slider(
        label="Max Return % clip", min_value=200, max_value=5000,
        value=2000, step=100,
    )

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(
    "<h1 style='"
    "font-family:\"Open Sans\",sans-serif;"
    "font-size:36px;font-weight:800;"
    "color:#e2e8f0;margin:0;padding:0"
    "'>Market <span style=\"color:#00f5d4\">Overview</span></h1>"
    "<p style='font-family:JetBrains Mono,monospace;color:#4a5568;font-size:13px;"
    "margin-top:4px;margin-bottom:24px'>Page 1 of 5  ·  Risk · Return · Structure · Similarity</p>",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════
#  KPI ROW
# ══════════════════════════════════════════════════════════════
sf_all_periods = s[s["cap_tier"].isin(selected_tiers)] if selected_tiers else s.copy()
n_total_in_tier = len(sf_all_periods)

# "All" uses total_ret_pct which exists for every coin — no date-window exclusion
if period_sel == "All":
    sf = sf_all_periods.copy()
else:
    sf = sf_all_periods[sf_all_periods[period_col].notna()].copy()

# FIX: ensure period_col always exists in sf (guard for edge cases)
if period_col not in sf.columns:
    sf[period_col] = float("nan")

n_period = len(sf)

k1, k2, k3, k4, k5, k6 = st.columns(6)

total_mcap   = sf["market_cap"].sum()
median_ret   = sf[period_col].median()
best_coin    = sf.loc[sf[period_col].idxmax(), "symbol"] if not sf.empty and sf[period_col].notna().any() else "—"
best_ret     = sf[period_col].max()
worst_coin   = sf.loc[sf[period_col].idxmin(), "symbol"] if not sf.empty and sf[period_col].notna().any() else "—"
worst_ret    = sf[period_col].min()
n_positive   = (sf[period_col] > 0).sum()
pct_positive = n_positive / len(sf) * 100 if len(sf) else 0

k1.metric("Total Mkt Cap",   f"${total_mcap/1e9:.1f}B")
k2.metric(f"Median {period_sel} Ret", f"{median_ret:.1f}%",
          delta=f"{'+' if median_ret>0 else ''}{median_ret:.1f}%")
k3.metric("🚀 Best",   f"{best_coin}",  delta=f"{best_ret:.0f}%")
k4.metric("💀 Worst",  f"{worst_coin}", delta=f"{worst_ret:.0f}%")
k5.metric("% Positive",     f"{pct_positive:.0f}%",
          delta=f"{n_positive}/{len(sf)}")
k6.metric(
    f"Coins w/ {period_sel} data",
    f"{n_period}",
    delta="all coins included" if period_sel == "All" else f"{n_period - n_total_in_tier} vs all tiers",
    help="All coins included regardless of launch date" if period_sel == "All"
         else f"{n_total_in_tier - n_period} coins excluded — launched after the {period_sel} cutoff",
)

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CHART TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "⬤  Risk vs Return",
    "▮  Tier Breakdown",
    "📈  Coin Price Chart",
    "🔗  Similarity Engine",
])

# ──────────────────────────────────────────────────────────────
#  TAB 1 │ BUBBLE — Risk vs Return
# ──────────────────────────────────────────────────────────────
with tab1:
    fig = go.Figure()
    plot_data = sf.copy()

    # FIX: ensure all period ret columns exist (some may be null for short-history coins)
    for _pc in ["ret_1M","ret_3M","ret_6M","ret_1Y","ret_3Y","ret_4Y","total_ret_pct"]:
        if _pc not in plot_data.columns:
            plot_data[_pc] = float("nan")

    for tier in selected_tiers:
        sub = plot_data[plot_data["cap_tier"] == tier].copy()
        if sub.empty:
            continue

        sub_x  = sub["volatility"].clip(upper=vol_clip)
        sub_y  = sub[period_col].clip(lower=-300, upper=ret_clip_max)
        sub_sz = np.log1p(sub["market_cap"].clip(lower=1e4)) * 2.8

        fig.add_trace(go.Scatter(
            x           = sub_x,
            y           = sub_y,
            mode        = "markers",
            name        = tier.upper(),
            legendgroup = tier,
            marker      = dict(
                size     = sub_sz,
                sizemode = "area",
                color    = TIER_COLORS.get(tier, ACCENT),
                opacity  = 0.82,
                line     = dict(width=0.8, color="rgba(255,255,255,0.2)"),
            ),
            text        = sub["symbol"],
            customdata  = np.stack([
                sub["name"],
                sub["ret_1M"].round(1),
                sub["ret_3M"].round(1),
                sub["ret_6M"].round(1),
                sub["ret_1Y"].round(1),
                sub["ret_3Y"].round(1),
                sub["ret_4Y"].round(1),
                sub["volatility"].round(4),
                sub["sharpe_proxy"].round(2),
                sub["market_cap"].apply(lambda x: f"${x/1e6:.1f}M"),
                sub[period_col].round(1),
            ], axis=-1),
            hovertemplate=(
                "<b>%{text}</b>  ·  %{customdata[0]}<br>"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                f"<b>{period_sel} Return : %{{customdata[10]}}%</b><br>"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                "1M : %{customdata[1]}%  │  3M : %{customdata[2]}%<br>"
                "6M : %{customdata[3]}%  │  1Y : %{customdata[4]}%<br>"
                "3Y : %{customdata[5]}%  │  4Y : %{customdata[6]}%<br>"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━<br>"
                "Volatility : %{customdata[7]}<br>"
                "Sharpe≈    : %{customdata[8]}<br>"
                "Mkt Cap    : %{customdata[9]}"
                "<extra></extra>"
            ),
        ))

    fig.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dot"))
    fig.add_vline(
        x=float(plot_data["volatility"].clip(upper=vol_clip).median()),
        line=dict(color=GOLD, width=1.2, dash="dash"),
        annotation_text="median vol",
        annotation_font=dict(color=GOLD, size=10),
        annotation_position="top right",
    )

    for qx, qy, qtxt in [
        (vol_clip * 0.88,  ret_clip_max * 0.88, "🚀 High Risk · High Return"),
        (vol_clip * 0.02,  ret_clip_max * 0.88, "💎 Low Risk · High Return"),
        (vol_clip * 0.88, -260,                 "💀 High Risk · Low Return"),
        (vol_clip * 0.02, -260,                 "😴 Low Risk · Low Return"),
    ]:
        fig.add_annotation(
            x=qx, y=qy, text=qtxt, showarrow=False,
            font=dict(color="rgba(255,255,255,0.13)", size=11, family="JetBrains Mono"),
        )

    fig.update_layout(
        **BASE_LAYOUT,
        title  = title_cfg(f"◈  Risk vs Return  ·  {period_sel} View  ·  {len(plot_data)} Coins"),
        height = 620,
        showlegend = True,
        legend = dict(
            title       = dict(text="Cap Tier", font=dict(color=ACCENT)),
            orientation = "v", x=0.01, y=0.99,
            bgcolor     = "rgba(0,0,0,0.6)",
            bordercolor = "#1e2d45", borderwidth=1,
        ),
        xaxis  = dict(title=dict(text=f"Daily Volatility  (σ, clipped @{vol_clip})", font=dict(color=MUTED)), **AXIS),
        yaxis  = dict(title=dict(text=f"Return %  —  {period_sel}", font=dict(color=MUTED)), **AXIS),
    )
    st.plotly_chart(fig, use_container_width=True)

    # FIX: "All" maps to "All%" column added to disp; all other periods map to "{period_sel}%"
    active_col_display = f"{period_sel}%"
    tiers_label = ", ".join(t.upper() for t in selected_tiers) if selected_tiers else "None"

    with st.expander(
        f"📋  Winners Table  ·  Period: {period_sel}  ·  Tiers: {tiers_label}  ·  {len(plot_data)} coins",
        expanded=False,
    ):
        st.markdown(
            f"<div style='display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap'>"
            + "".join(
                f"<span style='background:{TIER_COLORS.get(t,ACCENT)};color:#fff;"
                f"font-size:10px;font-family:JetBrains Mono;padding:3px 10px;"
                f"border-radius:20px;letter-spacing:1px'>{t.upper()}</span>"
                for t in selected_tiers
            )
            + f"<span style='background:#1e2d45;color:{GOLD};"
              f"font-size:10px;font-family:JetBrains Mono;padding:3px 10px;"
              f"border-radius:20px;letter-spacing:1px'>📅 {period_sel} ACTIVE</span>"
            + "</div>",
            unsafe_allow_html=True,
        )

        # FIX: include total_ret_pct and rename to "All%" so active_col_display works for all periods
        disp_cols = [
            "symbol", "name", "cap_tier", "volatility",
            "ret_1M", "ret_3M", "ret_6M", "ret_1Y",
            "ret_3Y", "ret_4Y", "total_ret_pct", "market_cap", "sharpe_proxy",
        ]
        # Ensure all display cols exist
        for _dc in disp_cols:
            if _dc not in plot_data.columns:
                plot_data[_dc] = float("nan")

        disp = (
            plot_data[disp_cols]
            .sort_values(period_col, ascending=False)
            .reset_index(drop=True)
        )
        disp.index += 1
        disp.columns = [
            "Symbol", "Name", "Tier", "Volatility",
            "1M%", "3M%", "6M%", "1Y%",
            "3Y%", "4Y%", "All%", "Mkt Cap", "Sharpe≈",
        ]
        disp["Mkt Cap"] = disp["Mkt Cap"].apply(lambda x: f"${x/1e6:.1f}M")

        # active_col_display = "{period_sel}%" which is now always a real column
        styled = (
            disp.style
            .background_gradient(
                subset=[active_col_display], cmap="RdYlGn",
                vmin=disp[active_col_display].quantile(0.05),
                vmax=disp[active_col_display].quantile(0.95),
            )
            .set_properties(
                subset=[active_col_display],
                **{"font-weight":"bold","border-left":"2px solid #ffd60a","border-right":"2px solid #ffd60a"},
            )
            .format({
                "Volatility":"{:.4f}","Sharpe≈":"{:.3f}",
                "1M%":"{:.1f}","3M%":"{:.1f}","6M%":"{:.1f}",
                "1Y%":"{:.1f}","3Y%":"{:.1f}","4Y%":"{:.1f}","All%":"{:.1f}",
            }, na_rep="—")
        )
        st.dataframe(styled, use_container_width=True, height=420)

        c_w, c_l = st.columns(2)
        with c_w:
            st.markdown(f"<div style='font-size:11px;color:{ACCENT};margin-bottom:6px;text-transform:uppercase;letter-spacing:1px'>🚀 Top 5  ·  {period_sel}</div>", unsafe_allow_html=True)
            st.dataframe(disp.head(5)[["Symbol","Tier",active_col_display]], use_container_width=True, hide_index=False, height=210)
        with c_l:
            st.markdown(f"<div style='font-size:11px;color:{ACCENT2};margin-bottom:6px;text-transform:uppercase;letter-spacing:1px'>💀 Bottom 5  ·  {period_sel}</div>", unsafe_allow_html=True)
            st.dataframe(disp.tail(5)[["Symbol","Tier",active_col_display]], use_container_width=True, hide_index=False, height=210)


# ──────────────────────────────────────────────────────────────
#  TAB 2 │ TIER BREAKDOWN
# ──────────────────────────────────────────────────────────────
with tab2:
    # FIX: guard against period_col missing from sf before groupby agg
    _tab2_df = sf[sf["cap_tier"].isin(available_tiers)].copy()
    if period_col not in _tab2_df.columns:
        _tab2_df[period_col] = float("nan")

    tier_stats = (
        _tab2_df
        .groupby("cap_tier", sort=False)
        .agg(
            count      = ("coin_id",      "count"),
            avg_ret    = (period_col,     "mean"),
            med_vol    = ("volatility",   "median"),
            med_sharpe = ("sharpe_proxy", "median"),
        )
        .reset_index()
        .set_index("cap_tier")
        .reindex(available_tiers)
        .dropna(subset=["count"])
        .reset_index()
    )

    fig3 = make_subplots(
        rows=1, cols=3,
        subplot_titles=["Coin Count by Tier", f"Avg {period_sel} Return %", "Median Volatility"],
        horizontal_spacing=0.10,
    )

    bar_colors = [TIER_COLORS.get(t, ACCENT) for t in tier_stats["cap_tier"]]
    ret_colors = [ACCENT2 if v < 0 else ACCENT for v in tier_stats["avg_ret"]]

    fig3.add_trace(go.Bar(
        x=tier_stats["cap_tier"].str.upper(), y=tier_stats["count"],
        marker=dict(color=bar_colors, opacity=0.9, line=dict(width=0)),
        text=tier_stats["count"], textposition="outside",
        textfont=dict(color=TEXT, size=13, family="JetBrains Mono"),
        customdata=tier_stats["med_vol"].round(4),
        hovertemplate="<b>%{x}</b><br>Coins : %{y}<br>Median Vol : %{customdata}<extra></extra>",
        showlegend=False,
    ), row=1, col=1)

    fig3.add_trace(go.Bar(
        x=tier_stats["cap_tier"].str.upper(), y=tier_stats["avg_ret"].round(1),
        marker=dict(color=ret_colors, opacity=0.85, line=dict(width=0)),
        text=(tier_stats["avg_ret"].round(1).astype(str) + "%"), textposition="outside",
        textfont=dict(color=TEXT, size=13, family="JetBrains Mono"),
        hovertemplate=f"<b>%{{x}}</b><br>Avg {period_sel} Return : %{{y:.1f}}%<extra></extra>",
        showlegend=False,
    ), row=1, col=2)
    fig3.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dot"), row=1, col=2)

    fig3.add_trace(go.Bar(
        x=tier_stats["cap_tier"].str.upper(), y=tier_stats["med_vol"].round(4),
        marker=dict(color=tier_stats["med_vol"], colorscale=[[0,"#0077b6"],[1,"#f72585"]], opacity=0.85, line=dict(width=0)),
        text=tier_stats["med_vol"].round(4), textposition="outside",
        textfont=dict(color=TEXT, size=12, family="JetBrains Mono"),
        hovertemplate="<b>%{x}</b><br>Median Volatility : %{y:.4f}<extra></extra>",
        showlegend=False,
    ), row=1, col=3)

    fig3.update_layout(
        paper_bgcolor=BG, plot_bgcolor=GRID,
        font=dict(family="JetBrains Mono, monospace", color=TEXT, size=12),
        title=title_cfg(f"◈  Cap Tier Breakdown  ·  {period_sel} Performance"),
        height=480, margin=dict(t=70, b=50, l=50, r=30),
    )
    fig3.update_xaxes(tickfont=dict(color=MUTED), gridcolor="#1a2540", zerolinecolor="#1a2540")
    fig3.update_yaxes(tickfont=dict(color=MUTED), gridcolor="#1a2540", zerolinecolor="#1a2540")
    for ann in fig3.layout.annotations:
        ann.font.color = ACCENT
        ann.font.size  = 13
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown(f"<div style='font-size:13px;color:{ACCENT};margin-bottom:12px'>◈  Return Distribution by Tier  ·  {period_sel}</div>", unsafe_allow_html=True)

    fig4 = go.Figure()
    for tier in selected_tiers:
        sub = sf[sf["cap_tier"] == tier]
        if sub.empty:
            continue
        fig4.add_trace(go.Violin(
            x=[tier.upper()] * len(sub),
            y=sub[period_col].clip(-300, ret_clip_max),
            name=tier.upper(), box_visible=True, meanline_visible=True,
            fillcolor=TIER_COLORS.get(tier, ACCENT), opacity=0.7,
            line_color="white", points="outliers",
        ))

    fig4.update_layout(
        **BASE_LAYOUT,
        title=title_cfg(f"Return Distribution  ·  {period_sel}"),
        height=380,
        xaxis=dict(**AXIS),
        yaxis=dict(title=dict(text=f"Return %  ({period_sel})", font=dict(color=MUTED)), **AXIS),
        showlegend=False,
    )
    fig4.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dot"))
    st.plotly_chart(fig4, use_container_width=True)


# ──────────────────────────────────────────────────────────────
#  TAB 3 │ COIN PRICE CHART
# ──────────────────────────────────────────────────────────────
with tab3:
    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])

    coin_options = (
        s.sort_values("market_cap", ascending=False)
        [["symbol", "name", "cap_tier"]]
        .drop_duplicates("symbol")
    )
    coin_labels = [
        f"{row.symbol}  ·  {row.name}  [{row.cap_tier.upper()}]"
        for row in coin_options.itertuples()
    ]

    with ctrl1:
        selected_label = st.selectbox("Select coin", options=coin_labels, index=0)
        selected_symbol = selected_label.split("  ·  ")[0].strip()
    with ctrl2:
        chart_type = st.radio("Chart type", options=["Line","Candlestick","OHLC"], index=0, horizontal=True)
    with ctrl3:
        date_range = st.selectbox("Date range", options=["1M","3M","6M","1Y","2Y","3Y","All"], index=3)

    matching_ids = s[s["symbol"] == selected_symbol]["coin_id"].unique().tolist()
    if not matching_ids:
        st.warning(f"No data found for symbol {selected_symbol}.")
    else:
        coin_id_sel = matching_ids[0]
        coin_df = df.filter(pl.col("coin_id") == coin_id_sel).sort("date").to_pandas()
        coin_df["date"] = pd.to_datetime(coin_df["date"])

        RANGE_DAYS = {"1M":30,"3M":90,"6M":180,"1Y":365,"2Y":730,"3Y":1095,"All":99999}
        cutoff = coin_df["date"].max() - pd.Timedelta(days=RANGE_DAYS[date_range])
        coin_df = coin_df[coin_df["date"] >= cutoff]

        if coin_df.empty:
            st.warning(f"{selected_symbol} has no data in the selected date range.")
        else:
            first_close = coin_df["close"].iloc[0]
            last_close  = coin_df["close"].iloc[-1]
            period_ret  = (last_close - first_close) / first_close * 100

            ck1, ck2, ck3, ck4, ck5 = st.columns(5)
            ck1.metric("Current price",   f"${last_close:,.4f}" if last_close < 1 else f"${last_close:,.2f}")
            ck2.metric(f"{date_range} return", f"{period_ret:.1f}%", delta=f"{'+' if period_ret>0 else ''}{period_ret:.1f}%")
            ck3.metric("Range high", f"${coin_df['high'].max():,.4f}" if coin_df['high'].max()<1 else f"${coin_df['high'].max():,.2f}")
            ck4.metric("Range low",  f"${coin_df['low'].min():,.4f}"  if coin_df['low'].min()<1  else f"${coin_df['low'].min():,.2f}")
            ck5.metric("Data since", coin_df["date"].min().strftime("%Y-%m-%d"))

            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

            fig_coin = make_subplots(rows=2, cols=1, row_heights=[0.75,0.25], shared_xaxes=True, vertical_spacing=0.04)

            if chart_type == "Line":
                fig_coin.add_trace(go.Scatter(
                    x=coin_df["date"], y=coin_df["close"], mode="lines", name="Close",
                    line=dict(color=ACCENT, width=1.8), fill="tozeroy",
                    fillcolor="rgba(0,245,212,0.07)",
                    hovertemplate="%{x|%Y-%m-%d}<br>Close: $%{y:,.4f}<extra></extra>",
                ), row=1, col=1)
            elif chart_type == "Candlestick":
                fig_coin.add_trace(go.Candlestick(
                    x=coin_df["date"], open=coin_df["open"], high=coin_df["high"],
                    low=coin_df["low"], close=coin_df["close"], name=selected_symbol,
                    increasing_line_color=ACCENT, decreasing_line_color=ACCENT2,
                    increasing_fillcolor="rgba(0,245,212,0.6)", decreasing_fillcolor="rgba(247,37,133,0.6)",
                ), row=1, col=1)
            else:
                fig_coin.add_trace(go.Ohlc(
                    x=coin_df["date"], open=coin_df["open"], high=coin_df["high"],
                    low=coin_df["low"], close=coin_df["close"], name=selected_symbol,
                    increasing_line_color=ACCENT, decreasing_line_color=ACCENT2,
                ), row=1, col=1)

            vol_colors = [ACCENT if c >= o else ACCENT2 for c, o in zip(coin_df["close"], coin_df["open"])]
            fig_coin.add_trace(go.Bar(
                x=coin_df["date"], y=coin_df["volume_usd"], name="Volume USD",
                marker=dict(color=vol_colors, opacity=0.6),
                hovertemplate="%{x|%Y-%m-%d}<br>Vol: $%{y:,.0f}<extra></extra>", showlegend=False,
            ), row=2, col=1)

            if chart_type == "Line" and len(coin_df) >= 20:
                coin_df["ma20"] = coin_df["close"].rolling(20).mean()
                fig_coin.add_trace(go.Scatter(
                    x=coin_df["date"], y=coin_df["ma20"], mode="lines", name="20d MA",
                    line=dict(color=GOLD, width=1.2, dash="dot"),
                    hovertemplate="%{x|%Y-%m-%d}<br>20d MA: $%{y:,.4f}<extra></extra>",
                ), row=1, col=1)

            coin_name_full = coin_df["name"].iloc[0] if "name" in coin_df.columns else selected_symbol
            fig_coin.update_layout(
                **BASE_LAYOUT,
                title=title_cfg(f"◈  {selected_symbol}  ·  {coin_name_full}  ·  {date_range} view  ·  {chart_type}"),
                height=620, xaxis_rangeslider_visible=False, showlegend=True,
                legend=dict(orientation="h", x=0.01, y=1.02, bgcolor="rgba(0,0,0,0.5)", bordercolor="#1e2d45", borderwidth=1),
                xaxis2=dict(**AXIS, title=dict(text="Date", font=dict(color=MUTED))),
                yaxis=dict(**AXIS, title=dict(text="Price (USD)", font=dict(color=MUTED))),
                yaxis2=dict(**AXIS, title=dict(text="Volume", font=dict(color=MUTED))),
            )
            fig_coin.update_xaxes(gridcolor="#1a2540", zerolinecolor="#1a2540", tickfont=dict(color=MUTED, family="JetBrains Mono"))
            fig_coin.update_yaxes(gridcolor="#1a2540", zerolinecolor="#1a2540", tickfont=dict(color=MUTED, family="JetBrains Mono"))
            st.plotly_chart(fig_coin, use_container_width=True)

            with st.expander("📋  Raw OHLCV data", expanded=False):
                show_df = coin_df[["date","open","high","low","close","volume_usd","market_cap_usd"]].copy()
                show_df.columns = ["Date","Open","High","Low","Close","Volume USD","Mkt Cap USD"]
                show_df = show_df.sort_values("Date", ascending=False).reset_index(drop=True)
                st.dataframe(
                    show_df.style.format({
                        "Open":"{:,.4f}","High":"{:,.4f}","Low":"{:,.4f}","Close":"{:,.4f}",
                        "Volume USD":"{:,.0f}","Mkt Cap USD":"{:,.0f}",
                    }),
                    use_container_width=True, height=350,
                )


# ══════════════════════════════════════════════════════════════
#  TAB 4 │ PHASE 2 — SIMILARITY ENGINE
# ══════════════════════════════════════════════════════════════
with tab4:

    # ── Section header ────────────────────────────────────────
    st.markdown(
        "<h2 style='"
        "font-family:\"Open Sans\",sans-serif;font-size:26px;font-weight:800;"
        "color:#e2e8f0;margin:0 0 4px 0'>"
        "🔗 Similarity <span style=\"color:#00f5d4\">Engine</span></h2>"
        "<p style='font-family:JetBrains Mono,monospace;color:#4a5568;font-size:12px;"
        "margin-bottom:20px'>"
        "Pearson correlation on daily log returns  ·  top-10 most similar coins  ·  "
        "pattern overlap · seasonal alignment</p>",
        unsafe_allow_html=True,
    )

    # ── Controls ──────────────────────────────────────────────
    sc1, sc2, sc3 = st.columns([2, 1, 1])

    # Anchor coin selector — sorted by market cap
    anchor_options = (
        s.sort_values("market_cap", ascending=False)
        [["coin_id", "symbol", "name", "cap_tier"]]
        .drop_duplicates("coin_id")
    )
    anchor_labels = [
        f"{row.symbol}  ·  {row.name}  [{row.cap_tier.upper()}]"
        for row in anchor_options.itertuples()
    ]
    anchor_ids = anchor_options["coin_id"].tolist()

    with sc1:
        anchor_label_sel = st.selectbox(
            "Anchor coin",
            options=anchor_labels,
            index=0,
            key="sim_anchor",
            help="Find the top 10 coins most correlated with this one",
        )
        anchor_symbol = anchor_label_sel.split("  ·  ")[0].strip()
        anchor_id     = anchor_ids[anchor_labels.index(anchor_label_sel)]

    with sc2:
        sim_window = st.selectbox(
            "Correlation window",
            options=["3M","6M","1Y","2Y","3Y","All"],
            index=2,
            key="sim_window",
            help="Date window over which Pearson correlation is computed",
        )
        WIN_DAYS = {"3M":90,"6M":180,"1Y":365,"2Y":730,"3Y":1095,"All":9999}
        window_days = WIN_DAYS[sim_window]

    with sc3:
        show_seasonal = st.checkbox(
            "Show seasonal heatmaps",
            value=True,
            key="show_seasonal",
            help="Month × Year return heatmaps for anchor + best match",
        )

    st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)

    # ── Compute ───────────────────────────────────────────────
    with st.spinner(f"Computing correlations for {anchor_symbol} over {sim_window}…"):
        ret_pivot   = build_return_matrix(df, window_days)
        sim_results = compute_similarity(ret_pivot, anchor_id, top_n=10)

    if sim_results.empty:
        st.warning(f"Not enough overlapping data for {anchor_symbol} in the {sim_window} window.")
        st.stop()

    # Enrich with meta
    all_ids     = [anchor_id] + sim_results["coin_id"].tolist()
    meta        = get_coin_meta(s, all_ids)
    anchor_meta = meta.get(anchor_id, {"symbol": anchor_symbol, "name": "", "cap_tier": "—"})

    sim_results["symbol"]   = sim_results["coin_id"].map(lambda x: meta.get(x, {}).get("symbol", x))
    sim_results["name"]     = sim_results["coin_id"].map(lambda x: meta.get(x, {}).get("name", ""))
    sim_results["cap_tier"] = sim_results["coin_id"].map(lambda x: meta.get(x, {}).get("cap_tier", "—"))

    # ── KPI summary row ───────────────────────────────────────
    best_match     = sim_results.iloc[0]
    avg_corr_top10 = sim_results["correlation"].mean()
    avg_dir_top10  = sim_results["pct_same_dir"].mean()
    n_sig          = (sim_results["p_value"] < 0.05).sum()

    sk1, sk2, sk3, sk4 = st.columns(4)
    sk1.metric("Best Match",       best_match["symbol"],
               delta=f"r = {best_match['correlation']:.3f}")
    sk2.metric("Avg Top-10 Corr", f"{avg_corr_top10:.3f}")
    sk3.metric("Avg Same-Dir %",  f"{avg_dir_top10:.1f}%",
               help="% of days both coins moved in the same direction")
    sk4.metric("Significant (p<0.05)", f"{n_sig} / 10")

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Horizontal correlation bar chart ──────────────────────
    fig_bar = go.Figure()

    bar_y      = sim_results["symbol"].tolist()[::-1]
    bar_x      = sim_results["correlation"].tolist()[::-1]
    bar_dir    = sim_results["pct_same_dir"].tolist()[::-1]
    bar_tiers  = sim_results["cap_tier"].tolist()[::-1]
    bar_names  = sim_results["name"].tolist()[::-1]
    bar_pval   = sim_results["p_value"].tolist()[::-1]
    bar_nobs   = sim_results["n_obs"].tolist()[::-1]

    fig_bar.add_trace(go.Bar(
        x           = bar_x,
        y           = bar_y,
        orientation = "h",
        marker      = dict(
            color   = bar_x,
            colorscale = [
                [0.0,  "#3a0ca3"],
                [0.5,  "#4361ee"],
                [0.85, "#00f5d4"],
                [1.0,  "#ffd60a"],
            ],
            cmin    = 0.0,
            cmax    = 1.0,
            showscale = True,
            colorbar  = dict(
                title      = dict(text="Pearson r", font=dict(color=MUTED, size=11)),
                tickfont   = dict(color=MUTED, family="JetBrains Mono"),
                thickness  = 12,
                len        = 0.6,
            ),
            line    = dict(width=0),
        ),
        customdata  = list(zip(bar_names, bar_tiers, bar_dir, bar_pval, bar_nobs)),
        hovertemplate=(
            "<b>%{y}</b>  ·  %{customdata[0]}<br>"
            "Tier        : %{customdata[1]}<br>"
            "Pearson r   : %{x:.4f}<br>"
            "Same-dir %  : %{customdata[2]:.1f}%<br>"
            "p-value     : %{customdata[3]:.4f}<br>"
            "Shared obs  : %{customdata[4]}<extra></extra>"
        ),
        text        = [f"r={v:.3f}" for v in bar_x],
        textposition= "outside",
        textfont    = dict(color=TEXT, size=11, family="JetBrains Mono"),
    ))

    # Highlight anchor
    fig_bar.add_annotation(
        x=1.0, y=1.0, xref="paper", yref="paper",
        text=f"Anchor: <b>{anchor_symbol}</b>  [{anchor_meta['cap_tier'].upper()}]",
        showarrow=False, align="right",
        font=dict(color=GOLD, size=12, family="JetBrains Mono"),
        bgcolor="rgba(0,0,0,0.5)", bordercolor=GOLD, borderwidth=1,
        borderpad=6, xanchor="right", yanchor="top",
    )

    fig_bar.update_layout(
        **BASE_LAYOUT,
        title  = title_cfg(
            f"◈  Top-10 Most Correlated with {anchor_symbol}  ·  {sim_window} Window"
        ),
        height = 420,
        xaxis  = dict(
            title=dict(text="Pearson Correlation (r)", font=dict(color=MUTED)),
            range=[0, 1.12], **AXIS,
        ),
        yaxis  = axis_tf(color=TEXT, size=12),
        showlegend = False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    #  SECTION 2: NORMALIZED PRICE OVERLAY
    # ══════════════════════════════════════════════════════════
    st.markdown(
        f"<div style='font-size:13px;color:{ACCENT};margin-bottom:12px'>"
        f"◈  Normalized Price Overlay  ·  rebased to 100  ·  {sim_window} window</div>",
        unsafe_allow_html=True,
    )

    top_n_overlay = st.slider(
        "Coins to overlay",
        min_value=1, max_value=10, value=5, step=1,
        key="overlay_n",
        help="How many of the top similar coins to show alongside the anchor",
    )

    overlay_ids  = [anchor_id] + sim_results["coin_id"].head(top_n_overlay).tolist()
    overlay_syms = {cid: meta.get(cid, {}).get("symbol", cid) for cid in overlay_ids}

    # FIX: rebase_prices now guards against missing coin_ids in close_pivot
    rebased = rebase_prices(close_pivot, overlay_ids)

    fig_ov = go.Figure()

    OVERLAY_PALETTE = [
        "#ffd60a", "#00f5d4", "#f72585", "#4cc9f0",
        "#7209b7", "#4361ee", "#3a0ca3", "#560bad",
        "#480ca8", "#3f37c9", "#4895ef",
    ]

    for i, cid in enumerate(overlay_ids):
        if rebased.empty or cid not in rebased.columns:
            continue
        sym       = overlay_syms[cid]
        is_anchor = (cid == anchor_id)
        color     = GOLD if is_anchor else OVERLAY_PALETTE[i % len(OVERLAY_PALETTE)]
        width     = 2.4 if is_anchor else 1.4
        opacity   = 1.0 if is_anchor else 0.75

        corr_val = ""
        if not is_anchor:
            row_match = sim_results[sim_results["coin_id"] == cid]
            if not row_match.empty:
                corr_val = f"  r={row_match.iloc[0]['correlation']:.3f}"

        fig_ov.add_trace(go.Scatter(
            x    = rebased.index,
            y    = rebased[cid],
            mode = "lines",
            name = f"{'★ ' if is_anchor else ''}{sym}{corr_val}",
            line = dict(color=color, width=width),
            opacity = opacity,
            hovertemplate=f"{sym}<br>%{{x|%Y-%m-%d}}<br>Indexed: %{{y:.1f}}<extra></extra>",
        ))

    fig_ov.add_hline(y=100, line=dict(color=MUTED, width=1, dash="dot"))

    fig_ov.update_layout(
        **BASE_LAYOUT,
        title  = title_cfg(
            f"◈  Price Pattern Overlap  ·  {anchor_symbol} + Top-{top_n_overlay} Similar  ·  {sim_window}"
        ),
        height = 500,
        showlegend = True,
        legend = dict(
            orientation = "v", x=0.01, y=0.99,
            bgcolor     = "rgba(0,0,0,0.65)",
            bordercolor = "#1e2d45", borderwidth=1,
            font        = dict(size=11, family="JetBrains Mono"),
        ),
        xaxis  = dict(**AXIS, title=dict(text="Date", font=dict(color=MUTED))),
        yaxis  = dict(**AXIS, title=dict(text="Indexed Price (base = 100)", font=dict(color=MUTED))),
    )
    st.plotly_chart(fig_ov, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    #  SECTION 3: ROLLING CORRELATION OVER TIME
    # ══════════════════════════════════════════════════════════
    st.markdown(
        f"<div style='font-size:13px;color:{ACCENT};margin-bottom:12px'>"
        f"◈  Rolling 90-Day Correlation  ·  {anchor_symbol} vs Top-5 Matches</div>",
        unsafe_allow_html=True,
    )

    top5_ids  = sim_results["coin_id"].head(5).tolist()
    top5_syms = {cid: meta.get(cid, {}).get("symbol", cid) for cid in top5_ids}

    # Build daily log-return series for anchor + top-5
    anchor_ret = ret_pivot[anchor_id].dropna() if anchor_id in ret_pivot.columns else pd.Series(dtype=float)

    fig_roll = go.Figure()
    ROLL_WIN = 90

    for i, cid in enumerate(top5_ids):
        if cid not in ret_pivot.columns:
            continue
        other_ret = ret_pivot[cid].dropna()
        common    = anchor_ret.index.intersection(other_ret.index)
        if len(common) < ROLL_WIN + 10:
            continue

        combined = pd.DataFrame({
            "anchor": anchor_ret.loc[common],
            "other":  other_ret.loc[common],
        }).dropna()

        rolling_corr = combined["anchor"].rolling(ROLL_WIN).corr(combined["other"])

        sym   = top5_syms[cid]
        color = OVERLAY_PALETTE[(i + 1) % len(OVERLAY_PALETTE)]

        fig_roll.add_trace(go.Scatter(
            x    = rolling_corr.index,
            y    = rolling_corr.values,
            mode = "lines",
            name = sym,
            line = dict(color=color, width=1.6),
            hovertemplate=f"{anchor_symbol}↔{sym}<br>%{{x|%Y-%m-%d}}<br>90d Corr: %{{y:.3f}}<extra></extra>",
        ))

    fig_roll.add_hline(y=0,   line=dict(color=MUTED, width=1, dash="dot"))
    fig_roll.add_hline(y=0.7, line=dict(color=GOLD,  width=0.8, dash="dash"),
                       annotation_text="r=0.7", annotation_font=dict(color=GOLD, size=10),
                       annotation_position="right")

    fig_roll.update_layout(
        **BASE_LAYOUT,
        title  = title_cfg(
            f"◈  Rolling 90d Correlation  ·  {anchor_symbol} vs Top-5  ·  Regime Changes Visible"
        ),
        height = 420,
        showlegend = True,
        legend = dict(
            orientation="h", x=0.01, y=1.02,
            bgcolor="rgba(0,0,0,0.6)", bordercolor="#1e2d45", borderwidth=1,
            font=dict(size=11, family="JetBrains Mono"),
        ),
        xaxis  = dict(**AXIS, title=dict(text="Date", font=dict(color=MUTED))),
        yaxis  = dict(**AXIS,
                      title=dict(text="Pearson r  (90d rolling)", font=dict(color=MUTED)),
                      range=[-1.1, 1.1]),
    )
    st.plotly_chart(fig_roll, use_container_width=True)

    # ══════════════════════════════════════════════════════════
    #  SECTION 4: SEASONAL HEATMAPS  (month × year)
    # ══════════════════════════════════════════════════════════
    if show_seasonal:
        st.markdown("---")
        st.markdown(
            f"<div style='font-size:13px;color:{ACCENT};margin-bottom:12px'>"
            f"◈  Seasonal Return Heatmap  ·  Month × Year  ·  "
            f"{anchor_symbol}  vs  {best_match['symbol']}</div>",
            unsafe_allow_html=True,
        )

        sh_col1, sh_col2 = st.columns(2)

        def render_seasonal_heatmap(coin_id_h, title_h):
            seas = seasonal_monthly_returns(df_pd, coin_id_h)
            if seas.empty:
                return None

            z_vals = seas.values
            x_vals = [str(c) for c in seas.columns.tolist()]
            y_vals = seas.index.tolist()

            fig_s = go.Figure(go.Heatmap(
                z          = z_vals,
                x          = x_vals,
                y          = y_vals,
                colorscale = [
                    [0.0,  "#f72585"],
                    [0.35, "#3a0ca3"],
                    [0.5,  "#1e2d45"],
                    [0.65, "#4361ee"],
                    [1.0,  "#00f5d4"],
                ],
                zmid       = 0,
                text       = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z_vals],
                texttemplate = "%{text}",
                textfont   = dict(size=10, family="JetBrains Mono", color="white"),
                hovertemplate="%{y} %{x}<br>Return: %{z:.1f}%<extra></extra>",
                showscale  = True,
                colorbar   = dict(
                    title     = dict(text="Ret %", font=dict(color=MUTED, size=10)),
                    tickfont  = dict(color=MUTED, family="JetBrains Mono", size=10),
                    thickness = 10,
                    len       = 0.8,
                ),
            ))
            fig_s.update_layout(
                paper_bgcolor = BG,
                plot_bgcolor  = GRID,
                title         = title_cfg(title_h, size=14),
                height        = 400,
                margin        = dict(t=50, b=30, l=60, r=40),
                font          = dict(family="JetBrains Mono", color=TEXT, size=11),
                xaxis         = dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540"),
                yaxis         = dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540", autorange="reversed"),
            )
            return fig_s

        with sh_col1:
            fig_s_anchor = render_seasonal_heatmap(
                anchor_id,
                f"◈  {anchor_symbol}  ·  Monthly Returns",
            )
            if fig_s_anchor:
                st.plotly_chart(fig_s_anchor, use_container_width=True)
            else:
                st.info(f"No seasonal data for {anchor_symbol}.")

        with sh_col2:
            best_cid = sim_results.iloc[0]["coin_id"]
            best_sym = sim_results.iloc[0]["symbol"]
            fig_s_best = render_seasonal_heatmap(
                best_cid,
                f"◈  {best_sym}  ·  Monthly Returns  (r={best_match['correlation']:.3f})",
            )
            if fig_s_best:
                st.plotly_chart(fig_s_best, use_container_width=True)
            else:
                st.info(f"No seasonal data for {best_sym}.")

        # Seasonal diff heatmap: anchor minus best match
        st.markdown(
            f"<div style='font-size:12px;color:{MUTED};margin-top:8px;margin-bottom:8px'>"
            f"◈  Δ Return Heatmap  ·  {anchor_symbol}  −  {best_sym}  "
            f"(green = anchor outperformed)</div>",
            unsafe_allow_html=True,
        )

        seas_a = seasonal_monthly_returns(df_pd, anchor_id)
        seas_b = seasonal_monthly_returns(df_pd, best_cid)
        if not seas_a.empty and not seas_b.empty:
            common_years = seas_a.columns.intersection(seas_b.columns)
            diff_hm = seas_a[common_years] - seas_b[common_years]

            fig_diff = go.Figure(go.Heatmap(
                z          = diff_hm.values,
                x          = [str(c) for c in common_years],
                y          = diff_hm.index.tolist(),
                colorscale = [
                    [0.0, "#f72585"],
                    [0.5, "#1e2d45"],
                    [1.0, "#00f5d4"],
                ],
                zmid       = 0,
                text       = [[f"{v:+.1f}%" if not np.isnan(v) else "" for v in row] for row in diff_hm.values],
                texttemplate = "%{text}",
                textfont   = dict(size=10, family="JetBrains Mono", color="white"),
                hovertemplate="%{y} %{x}<br>Δ: %{z:.1f}%<extra></extra>",
                showscale  = True,
                colorbar   = dict(
                    title     = dict(text="Δ Ret %", font=dict(color=MUTED, size=10)),
                    tickfont  = dict(color=MUTED, family="JetBrains Mono", size=10),
                    thickness = 10,
                ),
            ))
            fig_diff.update_layout(
                paper_bgcolor = BG,
                plot_bgcolor  = GRID,
                title         = title_cfg(
                    f"◈  Δ Return  ·  {anchor_symbol} − {best_sym}  ·  Month × Year",
                    size=14,
                ),
                height = 400,
                margin = dict(t=50, b=30, l=60, r=40),
                font   = dict(family="JetBrains Mono", color=TEXT, size=11),
                xaxis  = dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540"),
                yaxis  = dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540", autorange="reversed"),
            )
            st.plotly_chart(fig_diff, use_container_width=True)

    # ── Full similarity table ──────────────────────────────────
    st.markdown("---")
    with st.expander(
        f"📋  Full Similarity Table  ·  {anchor_symbol}  ·  Top-10  ·  {sim_window} window",
        expanded=True,
    ):
        disp_sim = sim_results[[
            "symbol", "name", "cap_tier", "correlation",
            "p_value", "n_obs", "pct_same_dir",
        ]].copy()
        disp_sim.columns = [
            "Symbol", "Name", "Tier", "Pearson r",
            "p-value", "Obs", "Same-Dir %",
        ]
        styled_sim = (
            disp_sim.style
            .background_gradient(subset=["Pearson r"], cmap="RdYlGn", vmin=0, vmax=1)
            .background_gradient(subset=["Same-Dir %"], cmap="Blues", vmin=50, vmax=100)
            .set_properties(
                subset=["Pearson r"],
                **{"font-weight": "bold", "border-left": "2px solid #ffd60a", "border-right": "2px solid #ffd60a"},
            )
            .format({
                "Pearson r":   "{:.4f}",
                "p-value":     "{:.4f}",
                "Same-Dir %":  "{:.1f}%",
            })
        )
        st.dataframe(styled_sim, use_container_width=True, height=360)

# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;font-size:11px;color:{MUTED};"
    f"font-family:JetBrains Mono,monospace;padding:12px'>"
    f"◈  Crypto Intelligence Dashboard  ·  "
    f"Data: {df['date'].min()} → {df['date'].max()}  ·  "
    f"{df['coin_id'].n_unique()} coins  ·  Built with Streamlit + Polars + Plotly"
    f"</div>",
    unsafe_allow_html=True,
)