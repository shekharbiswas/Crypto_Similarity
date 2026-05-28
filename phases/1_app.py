"""
╔══════════════════════════════════════════════════════════════╗
║   CRYPTO INTELLIGENCE DASHBOARD  —  Streamlit Edition        ║
║   Run:  streamlit run app.py                                 ║
║   Data: crypto_with_indicators.csv  (../data/ folder)       ║
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
import os
import tempfile  
import requests
import datetime




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
#  GLOBAL STYLES
# ══════════════════════════════════════════════════════════════

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;700;800&family=Open+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


st.markdown("""
<style>
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
    white-space: normal;        /* ← changed */
    overflow: visible;          /* ← changed */
    line-height: 1.3;           /* ← added */
}
[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    white-space: normal;
    overflow: visible;
    word-break: break-word; 
}
[data-testid="stMetricDelta"] { font-size: 16px !important; }
[data-testid="stMetric"] { min-height: 110px !important; }

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
            
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #00f5d4 !important;
}
            
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



@st.cache_data(show_spinner="⏳ Loading from HuggingFace... (first load ~30s)")
def load_data():
    import datetime
    # Step 1 — peek at the last date in the dataset
    _peek = pl.scan_parquet(
        "hf://datasets/shekharbiswas/crypto-indicators/crypto_with_indicators.parquet"
    ).select("date").max().collect()

    latest_date = datetime.date.fromisoformat(str(_peek["date"][0])[:10])

    # Step 2 — go 1Y back from the DATA's latest date, not today
    cutoff = latest_date - datetime.timedelta(days=365)

    df = (
        pl.scan_parquet("hf://datasets/shekharbiswas/crypto-indicators/crypto_with_indicators.parquet")
        .with_columns([
            pl.col("date").str.to_date("%Y-%m-%d"),
            pl.col("close").cast(pl.Float64),
            pl.col("open").cast(pl.Float64),
            pl.col("high").cast(pl.Float64),
            pl.col("low").cast(pl.Float64),
            pl.col("volume_usd").cast(pl.Float64),
            pl.col("market_cap_usd").cast(pl.Float64),
            pl.col("change_24h_pct").cast(pl.Float64),
            pl.col("is_stablecoin").cast(pl.Boolean),
            pl.col("EMA_9").cast(pl.Float64),
            pl.col("EMA_21").cast(pl.Float64),
            pl.col("EMA_50").cast(pl.Float64),
            pl.col("EMA_100").cast(pl.Float64),
            pl.col("EMA_200").cast(pl.Float64),
            pl.col("SMA_50").cast(pl.Float64),
            pl.col("SMA_200").cast(pl.Float64),
            pl.col("BB_Middle").cast(pl.Float64),
            pl.col("BB_Upper").cast(pl.Float64),
            pl.col("BB_Lower").cast(pl.Float64),
            pl.col("BB_Width").cast(pl.Float64),
            pl.col("BB_Percent").cast(pl.Float64),
            pl.col("KC_Middle").cast(pl.Float64),
            pl.col("KC_Upper").cast(pl.Float64),
            pl.col("KC_Lower").cast(pl.Float64),
            pl.col("DC_Upper").cast(pl.Float64),
            pl.col("DC_Lower").cast(pl.Float64),
            pl.col("DC_Middle").cast(pl.Float64),
            pl.col("Pivot").cast(pl.Float64),
            pl.col("R1").cast(pl.Float64),
            pl.col("S1").cast(pl.Float64),
            pl.col("R2").cast(pl.Float64),
            pl.col("S2").cast(pl.Float64),
            pl.col("VWAP").cast(pl.Float64),
            pl.col("Supertrend").cast(pl.Float64),
            pl.col("Supertrend_Direction").cast(pl.Int8),
            pl.col("PSAR").cast(pl.Float64),
            pl.col("PSAR_Trend").cast(pl.Int8),
            pl.col("Ichimoku_Tenkan").cast(pl.Float64),
            pl.col("Ichimoku_Kijun").cast(pl.Float64),
            pl.col("Ichimoku_SpanA").cast(pl.Float64),
            pl.col("Ichimoku_SpanB").cast(pl.Float64),
            pl.col("RSI").cast(pl.Float64),
            pl.col("Stoch_K").cast(pl.Float64),
            pl.col("Stoch_D").cast(pl.Float64),
            pl.col("Williams_R").cast(pl.Float64),
            pl.col("CCI").cast(pl.Float64),
            pl.col("ROC_9").cast(pl.Float64),
            pl.col("ROC_14").cast(pl.Float64),
            pl.col("ROC_21").cast(pl.Float64),
            pl.col("MACD").cast(pl.Float64),
            pl.col("MACD_Signal").cast(pl.Float64),
            pl.col("MACD_Hist").cast(pl.Float64),
            pl.col("TSI").cast(pl.Float64),
            pl.col("OBV").cast(pl.Float64),
            pl.col("AD_Line").cast(pl.Float64),
            pl.col("CMF").cast(pl.Float64),
            pl.col("MFI").cast(pl.Float64),
            pl.col("Volume_ROC").cast(pl.Float64),
            pl.col("ATR").cast(pl.Float64),
            pl.col("PLUS_DI").cast(pl.Float64),
            pl.col("MINUS_DI").cast(pl.Float64),
            pl.col("ADX").cast(pl.Float64),
            pl.col("Aroon_Up").cast(pl.Float64),
            pl.col("Aroon_Down").cast(pl.Float64),
            pl.col("Aroon_Oscillator").cast(pl.Float64),
            pl.col("Higher_Highs").cast(pl.Int8),
            pl.col("Higher_Lows").cast(pl.Int8),
            pl.col("Next_1d_Return").cast(pl.Float64),
            pl.col("Next_2d_Return").cast(pl.Float64),
            pl.col("Next_3d_Return").cast(pl.Float64),
            pl.col("Next_5d_Return").cast(pl.Float64),
            pl.col("Next_7d_Return").cast(pl.Float64),
            pl.col("surge_score").cast(pl.Float64),
            pl.col("cap_tier").cast(pl.Utf8),
        ])
        .filter(pl.col("is_stablecoin") == False)
        .filter(pl.col("date") >= pl.lit(cutoff))
        .sort(["coin_id", "date"])
        .collect()
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
#  PHASE 2: RETURN SIMILARITY ENGINE HELPERS
# ══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Building return matrix...")
def build_return_matrix(_df, window_days: int):
    pdf = _df.to_pandas()
    pdf["date"] = pd.to_datetime(pdf["date"])
    latest = pdf["date"].max()
    cutoff = latest - pd.Timedelta(days=window_days)
    pdf = pdf[pdf["date"] >= cutoff]
    pivot = pdf.pivot_table(index="date", columns="coin_id", values="log_ret")
    min_obs = int(0.8 * len(pivot))
    pivot = pivot.dropna(thresh=min_obs, axis=1)
    return pivot


def compute_similarity(pivot: pd.DataFrame, anchor_id: str, top_n: int = 10):
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
    valid_ids = [c for c in coin_ids if c in pivot_close.columns]
    if not valid_ids:
        return pd.DataFrame()
    sub = pivot_close[valid_ids].dropna(how="all")
    rebased = sub.div(sub.bfill().iloc[0]) * 100
    return rebased


def seasonal_monthly_returns(df_pd: pd.DataFrame, coin_id: str) -> pd.DataFrame:
    MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    sub = df_pd[df_pd["coin_id"] == coin_id].copy()
    sub["date"]  = pd.to_datetime(sub["date"])
    sub["year"]  = sub["date"].dt.year
    sub["month"] = sub["date"].dt.month
    monthly = (
        sub.groupby(["year", "month"])["log_ret"]
        .sum()
        .reset_index()
    )
    monthly["ret_pct"] = (np.exp(monthly["log_ret"]) - 1) * 100
    pivot = monthly.pivot(index="month", columns="year", values="ret_pct")
    pivot = pivot.reindex(range(1, 13))
    pivot.index = MONTH_NAMES
    return pivot


# ══════════════════════════════════════════════════════════════
#  PHASE 3: REGIME SIMILARITY HELPERS
# ══════════════════════════════════════════════════════════════

REGIME_FEATURES = [
    "RSI", "BB_Percent", "ADX", "PLUS_DI", "MINUS_DI",
    "Supertrend_Direction", "PSAR_Trend",
    "CMF", "MFI", "Aroon_Oscillator", "ema_stack",
]

REGIME_FEATURE_LABELS = {
    "RSI":                   "RSI (Momentum)",
    "BB_Percent":            "BB% (Band Position)",
    "ADX":                   "ADX (Trend Strength)",
    "PLUS_DI":               "+DI (Bull Pressure)",
    "MINUS_DI":              "−DI (Bear Pressure)",
    "Supertrend_Direction":  "Supertrend",
    "PSAR_Trend":            "Parabolic SAR",
    "CMF":                   "CMF (Money Flow)",
    "MFI":                   "MFI (Money Flow Index)",
    "Aroon_Oscillator":      "Aroon Oscillator",
    "ema_stack":             "EMA Stack (9/21/50)",
}


@st.cache_data(show_spinner="Building regime snapshot...")
def build_regime_snapshot(_df, _s):
    """
    Latest technical state per coin — one row per coin.
    Derives ema_stack: +1 = fully bullish (9>21>50), -1 = fully bearish, 0 = mixed.
    """
    latest = (
        _df.sort("date")
        .group_by("coin_id")
        .agg([
            pl.col("RSI").last(),
            pl.col("BB_Percent").last(),
            pl.col("ADX").last(),
            pl.col("PLUS_DI").last(),
            pl.col("MINUS_DI").last(),
            pl.col("Supertrend_Direction").last().cast(pl.Float64),
            pl.col("PSAR_Trend").last().cast(pl.Float64),
            pl.col("CMF").last(),
            pl.col("MFI").last(),
            pl.col("Aroon_Oscillator").last(),
            pl.col("EMA_9").last(),
            pl.col("EMA_21").last(),
            pl.col("EMA_50").last(),
            pl.col("surge_score").last(),
            pl.col("date").max().alias("snapshot_date"),
        ])
        .to_pandas()
    )

    latest["ema_stack"] = np.where(
        (latest["EMA_9"] > latest["EMA_21"]) & (latest["EMA_21"] > latest["EMA_50"]),  1.0,
        np.where(
            (latest["EMA_9"] < latest["EMA_21"]) & (latest["EMA_21"] < latest["EMA_50"]), -1.0,
            0.0
        )
    )

    meta = _s[["coin_id","symbol","name","cap_tier","market_cap"]].drop_duplicates("coin_id")
    latest = latest.merge(meta, on="coin_id", how="left")
    return latest


def compute_regime_similarity(snapshot_df: pd.DataFrame, anchor_id: str,
                               selected_tiers: list, top_n: int = 10):
    """
    Cosine similarity on z-score normalised regime feature vector.
    Returns (sim_df, anchor_raw_row).
    """
    df = snapshot_df[snapshot_df["cap_tier"].isin(selected_tiers)].copy()
    feat_df = df[["coin_id"] + REGIME_FEATURES].dropna().reset_index(drop=True)

    if anchor_id not in feat_df["coin_id"].values:
        return pd.DataFrame(), pd.DataFrame()

    feat_vals = feat_df[REGIME_FEATURES].copy().astype(float)
    for f in REGIME_FEATURES:
        std = feat_vals[f].std()
        feat_vals[f] = (feat_vals[f] - feat_vals[f].mean()) / std if std > 0 else 0.0
    feat_df[REGIME_FEATURES] = feat_vals

    anchor_vec = feat_df.loc[feat_df["coin_id"] == anchor_id, REGIME_FEATURES].values[0]

    results = []
    for _, row in feat_df.iterrows():
        if row["coin_id"] == anchor_id:
            continue
        other_vec = row[REGIME_FEATURES].values.astype(float)
        norm = np.linalg.norm(anchor_vec) * np.linalg.norm(other_vec)
        cos_sim = float(np.dot(anchor_vec, other_vec) / norm) if norm > 0 else 0.0
        results.append({"coin_id": row["coin_id"], "cosine_sim": cos_sim})

    if not results:
        return pd.DataFrame(), pd.DataFrame()

    res = (
        pd.DataFrame(results)
        .sort_values("cosine_sim", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    res.index += 1

    raw = snapshot_df[["coin_id","symbol","name","cap_tier","surge_score"] + REGIME_FEATURES]
    res = res.merge(raw, on="coin_id", how="left")

    anchor_raw = snapshot_df[snapshot_df["coin_id"] == anchor_id]
    return res, anchor_raw


# ── Regime label helpers ─────────────────────────────────────

def rsi_label(rsi):
    if pd.isna(rsi):   return "N/A",        MUTED
    if rsi < 30:       return "OVERSOLD",    ACCENT2
    if rsi > 70:       return "OVERBOUGHT",  GOLD
    return "NEUTRAL", ACCENT

def adx_label(adx):
    if pd.isna(adx):  return "N/A",           MUTED
    if adx < 20:      return "RANGING",        MUTED
    if adx < 40:      return "TRENDING",       ACCENT
    return "STRONG TREND", GOLD

def trend_label(st_dir, psar):
    if pd.isna(st_dir) or pd.isna(psar): return "N/A",     MUTED
    if st_dir == 1  and psar == 1:       return "BULLISH",  ACCENT
    if st_dir == -1 and psar == -1:      return "BEARISH",  ACCENT2
    return "MIXED", GOLD

def bb_label(bb_pct):
    if pd.isna(bb_pct): return "N/A",              MUTED
    if bb_pct < 0.2:    return "NEAR LOWER BAND",   ACCENT2
    if bb_pct > 0.8:    return "NEAR UPPER BAND",   GOLD
    return "MID BAND", ACCENT

def ema_stack_label(val):
    if pd.isna(val):  return "N/A",        MUTED
    if val == 1.0:    return "BULL STACK",  ACCENT
    if val == -1.0:   return "BEAR STACK",  ACCENT2
    return "MIXED",   GOLD


# ══════════════════════════════════════════════════════════════
#  PHASE 4: FORWARD RETURN LAB HELPERS
# ══════════════════════════════════════════════════════════════

def forward_return_in_regime(df_pd: pd.DataFrame, coin_id: str,
                              anchor_rsi: float, anchor_adx: float,
                              rsi_tol: float = 10.0, adx_tol: float = 10.0) -> pd.DataFrame:
    """
    Find historical dates where coin was in a similar RSI+ADX regime
    and return the distribution of subsequent forward returns.
    """
    sub = df_pd[df_pd["coin_id"] == coin_id].copy()
    sub["date"] = pd.to_datetime(sub["date"])
    similar = sub[
        sub["RSI"].between(anchor_rsi - rsi_tol, anchor_rsi + rsi_tol) &
        sub["ADX"].between(anchor_adx - adx_tol, anchor_adx + adx_tol)
    ]
    cols = ["date","RSI","ADX","surge_score",
            "Next_1d_Return","Next_2d_Return","Next_3d_Return",
            "Next_5d_Return","Next_7d_Return"]
    return similar[[c for c in cols if c in similar.columns]].dropna(
        subset=["Next_1d_Return","Next_5d_Return"]
    )


# ══════════════════════════════════════════════════════════════
#  LOAD
# ══════════════════════════════════════════════════════════════
try:
    df = load_data()
    s  = build_summary(df)

except Exception as e:
    st.error(f"❌ Error loading data: {type(e).__name__}: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

TIER_ORDER      = ["mega","large","mid","small","micro"]
available_tiers = [t for t in TIER_ORDER if t in s["cap_tier"].values]
PERIOD_COLS     = {"1M":"ret_1M","3M":"ret_3M","6M":"ret_6M",
                   "1Y":"ret_1Y","3Y":"ret_3Y","4Y":"ret_4Y",
                   "All":"total_ret_pct"}


@st.cache_data(show_spinner="Building close-price matrix...")
def build_close_matrix(_df):
    pdf = _df.to_pandas()
    pdf["date"] = pd.to_datetime(pdf["date"])
    return pdf.pivot_table(index="date", columns="coin_id", values="close")


close_pivot    = build_close_matrix(df)
df_pd          = df.to_pandas()
regime_snapshot = build_regime_snapshot(df, s)

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
        # options   = list(PERIOD_COLS.keys()),
        options = ["1M", "3M", "6M", "1Y"],
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
    "'>Crypto <span style=\"color:#00f5d4\">Intelligence</span></h1>"
    "<p style='font-family:JetBrains Mono,monospace;color:#4a5568;font-size:13px;"
    "margin-top:4px;margin-bottom:24px'>6 tabs  ·  Market Overview · Tier Breakdown · Coin Deep Dive · Return Similarity · Regime Similarity · Forward Return Lab</p>",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════
#  KPI ROW
# ══════════════════════════════════════════════════════════════
sf_all_periods = s[s["cap_tier"].isin(selected_tiers)] if selected_tiers else s.copy()
n_total_in_tier = len(sf_all_periods)

if period_sel == "All":
    sf = sf_all_periods.copy()
else:
    sf = sf_all_periods[sf_all_periods[period_col].notna()].copy()

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

k1.metric("Total Mkt Cap", f"${total_mcap/1e9:.1f}B",
          delta="sum across selected tiers",
          help="Sum of last-known market caps for all coins in the selected cap tiers.")
k2.metric(f"Median {period_sel} Ret", f"{median_ret:.1f}%",
          delta=f"{'+' if median_ret>0 else ''}{median_ret:.1f}%",
          help=f"Median {period_sel} return across all coins with sufficient history.")
k3.metric("🚀 Best", f"{best_coin}",
          delta=f"{best_ret:.0f}%",
          help=f"Coin with the highest {period_sel} return in the current selection.")
k4.metric("💀 Worst", f"{worst_coin}",
          delta=f"{worst_ret:.0f}%",
          help=f"Coin with the lowest {period_sel} return in the current selection.")
k5.metric("% Positive", f"{pct_positive:.0f}%",
          delta=f"{n_positive}/{len(sf)} coins",
          help=f"Share of coins posting a positive return over {period_sel}.")
k6.metric(f"Coins w/ {period_sel} data", f"{n_period}",
          delta="all coins included" if period_sel == "All" else f"{n_total_in_tier - n_period} excluded",
          help="All coins included regardless of launch date." if period_sel == "All"
               else f"{n_total_in_tier - n_period} coins excluded — launched after the {period_sel} cutoff.")

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⬤  Market Overview",
    "▮  Tier Breakdown",
    "📊  Coin Deep Dive",
    "🔗  Return Similarity",
    "🧭  Regime Similarity",
    "🔮  Forward Return Lab",
])

OVERLAY_PALETTE = [
    "#ffd60a", "#00f5d4", "#f72585", "#4cc9f0",
    "#7209b7", "#4361ee", "#3a0ca3", "#560bad",
    "#480ca8", "#3f37c9", "#4895ef",
]

# ──────────────────────────────────────────────────────────────
#  TAB 1 │ MARKET OVERVIEW  (Risk vs Return bubble)
# ──────────────────────────────────────────────────────────────
with tab1:
    st.markdown(
        "<h2 style='font-family:\"Open Sans\",sans-serif;font-size:26px;font-weight:800;"
        "color:#e2e8f0;margin:0 0 4px 0'>"
        "⬤ Market <span style='color:#00f5d4'>Overview</span></h2>",
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div style='background:#111827;border:1px solid #1e2d45;border-radius:10px;
    padding:16px 20px;margin-bottom:20px;font-family:JetBrains Mono,monospace'>
    <div style='color:#00f5d4;font-size:11px;text-transform:uppercase;
    letter-spacing:1px;margin-bottom:8px'>◈ How to read this chart</div>
    <div style='color:#94a3b8;font-size:13px;line-height:1.8'>
    Each <b style='color:#e2e8f0'>bubble</b> is one coin. The <b style='color:#e2e8f0'>x-axis</b>
    is daily return volatility (σ) — how wildly the price moves day-to-day.
    The <b style='color:#e2e8f0'>y-axis</b> is the selected return period.
    <b style='color:#e2e8f0'>Bubble size</b> scales with market cap (log-transformed so micro-caps
    remain visible). The <b style='color:{GOLD}'>gold dashed line</b> is the median volatility:
    coins to its right are riskier than average; coins above the zero line are profitable
    over the selected period. The ideal quadrant — low volatility, high return — is top-left.
    Use the <b style='color:#e2e8f0'>sidebar</b> to filter by cap tier, change the return period,
    and adjust volatility clipping.
    </div></div>
    """, unsafe_allow_html=True)

    fig = go.Figure()
    plot_data = sf.copy()

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
            x=sub_x, y=sub_y, mode="markers",
            name=tier.upper(), legendgroup=tier,
            marker=dict(
                size=sub_sz, sizemode="area",
                color=TIER_COLORS.get(tier, ACCENT), opacity=0.82,
                line=dict(width=0.8, color="rgba(255,255,255,0.2)"),
            ),
            text=sub["symbol"],
            customdata=np.stack([
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
        title=title_cfg(f"◈  Risk vs Return  ·  {period_sel} View  ·  {len(plot_data)} Coins"),
        height=620, showlegend=True,
        legend=dict(
            title=dict(text="Cap Tier", font=dict(color=ACCENT)),
            orientation="v", x=0.01, y=0.99,
            bgcolor="rgba(0,0,0,0.6)", bordercolor="#1e2d45", borderwidth=1,
        ),
        xaxis=dict(title=dict(text=f"Daily Volatility  (σ, clipped @{vol_clip})", font=dict(color=MUTED)), **AXIS),
        yaxis=dict(title=dict(text=f"Return %  —  {period_sel}", font=dict(color=MUTED)), **AXIS),
    )
    st.plotly_chart(fig, width='stretch')

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

        disp_cols = [
            "symbol","name","cap_tier","volatility",
            "ret_1M","ret_3M","ret_6M","ret_1Y",
            "ret_3Y","ret_4Y","total_ret_pct","market_cap","sharpe_proxy",
        ]
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
            "Symbol","Name","Tier","Volatility",
            "1M%","3M%","6M%","1Y%",
            "3Y%","4Y%","All%","Mkt Cap","Sharpe≈",
        ]
        disp["Mkt Cap"] = disp["Mkt Cap"].apply(lambda x: f"${x/1e6:.1f}M")

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
    st.markdown(
        "<h2 style='font-family:\"Open Sans\",sans-serif;font-size:26px;font-weight:800;"
        "color:#e2e8f0;margin:0 0 4px 0'>"
        "▮ Tier <span style='color:#00f5d4'>Breakdown</span></h2>",
        unsafe_allow_html=True,
    )
    st.markdown(f"""
    <div style='background:#111827;border:1px solid #1e2d45;border-radius:10px;
    padding:16px 20px;margin-bottom:20px;font-family:JetBrains Mono,monospace'>
    <div style='color:#00f5d4;font-size:11px;text-transform:uppercase;
    letter-spacing:1px;margin-bottom:8px'>◈ Cap tier definitions</div>
    <div style='color:#94a3b8;font-size:13px;line-height:1.8'>
    Coins are segmented by market capitalisation into five tiers:
    <b style='color:#f72585'>MEGA</b> (&gt;$100B),
    <b style='color:#7209b7'>LARGE</b> ($10B–$100B),
    <b style='color:#3a0ca3'>MID</b> ($1B–$10B),
    <b style='color:#4361ee'>SMALL</b> ($100M–$1B), and
    <b style='color:#4cc9f0'>MICRO</b> (&lt;$100M).
    The three bar charts show, for the selected return period:
    how many coins sit in each tier (left), their average return (centre),
    and their median daily volatility (right).
    The violin plot below shows the full return distribution — not just averages —
    revealing skew, outliers, and whether gains are concentrated in a few coins
    or broadly distributed. Wide violins = many coins at that return level.
    </div></div>
    """, unsafe_allow_html=True)

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
    st.plotly_chart(fig3, width='stretch')

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
    st.plotly_chart(fig4, width='stretch')


# ──────────────────────────────────────────────────────────────
#  TAB 3 │ COIN DEEP DIVE  (price + RSI + MACD + regime cards)
# ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown(
        "<h2 style='font-family:\"Open Sans\",sans-serif;font-size:24px;font-weight:800;"
        "color:#e2e8f0;margin:0 0 4px 0'>"
        "📊 Coin <span style='color:#00f5d4'>Deep Dive</span></h2>",
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style='background:#111827;border:1px solid #1e2d45;border-radius:10px;
    padding:16px 20px;margin-bottom:20px;font-family:JetBrains Mono,monospace'>
    <div style='color:#00f5d4;font-size:11px;text-transform:uppercase;
    letter-spacing:1px;margin-bottom:8px'>◈ How to read this tab</div>
    <div style='color:#94a3b8;font-size:13px;line-height:1.8'>
    This tab gives a complete single-coin picture across price action, momentum, and trend.
    The <b style='color:#e2e8f0'>price chart</b> (top panel) shows OHLC with an optional 20-day MA.
    The <b style='color:#e2e8f0'>RSI panel</b> highlights overbought (&gt;70, gold zone) and oversold
    (&lt;30, red zone) conditions — readings at the extremes often precede mean-reversion moves.
    RSI between 30–70 is considered neutral territory with no directional edge.
    The <b style='color:#e2e8f0'>MACD panel</b> shows momentum crossovers: when the MACD line crosses
    above the signal line the histogram turns teal (bullish momentum accelerating); crossing below
    turns red (bearish). The histogram height measures the gap between the two lines — a widening gap
    means momentum is strengthening in that direction.
    The <b style='color:#00f5d4'>Regime State cards</b> beneath the chart summarise the coin's
    <i>current</i> technical posture across six independent signals in one glance — think of it
    as a one-line trading desk briefing.
    </div></div>
    """, unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])

    coin_options = (
        s[s["cap_tier"].isin(selected_tiers)]
        .sort_values("market_cap", ascending=False)
        [["symbol","name","cap_tier"]]
        .drop_duplicates("symbol")
    )
    coin_labels = [
        f"{r.symbol}  ·  {r.name}  [{r.cap_tier.upper()}]"
        for r in coin_options.itertuples()
    ]

    with ctrl1:
        selected_label  = st.selectbox("Select coin", options=coin_labels, index=0, key="dd_coin")
        selected_symbol = selected_label.split("  ·  ")[0].strip()
    with ctrl2:
        chart_type = st.radio("Chart type", ["Line","Candlestick","OHLC"], index=0, horizontal=True, key="dd_ct")
    with ctrl3:
        date_range = st.selectbox("Date range", ["1M","3M","6M","1Y","2Y","3Y","All"], index=3, key="dd_dr")

    matching_ids = s[s["symbol"] == selected_symbol]["coin_id"].unique().tolist()

    if not matching_ids:
        st.warning(f"No data found for {selected_symbol}.")
    else:
        coin_id_sel = matching_ids[0]
        coin_df = df.filter(pl.col("coin_id") == coin_id_sel).sort("date").to_pandas()
        coin_df["date"] = pd.to_datetime(coin_df["date"])

        RANGE_DAYS = {"1M":30,"3M":90,"6M":180,"1Y":365,"2Y":730,"3Y":1095,"All":99999}
        cutoff  = coin_df["date"].max() - pd.Timedelta(days=RANGE_DAYS[date_range])
        coin_df = coin_df[coin_df["date"] >= cutoff]

        if coin_df.empty:
            st.warning(f"{selected_symbol} has no data in the selected range.")
        else:
            first_close = coin_df["close"].iloc[0]
            last_close  = coin_df["close"].iloc[-1]
            period_ret  = (last_close - first_close) / first_close * 100

            ck1,ck2,ck3,ck4,ck5 = st.columns(5)
            ck1.metric("Current Price",
                       f"${last_close:,.4f}" if last_close < 1 else f"${last_close:,.2f}")
            ck2.metric(f"{date_range} Return", f"{period_ret:.1f}%",
                       delta=f"{'+' if period_ret>0 else ''}{period_ret:.1f}%")
            ck3.metric("Range High",
                       f"${coin_df['high'].max():,.4f}" if coin_df['high'].max()<1
                       else f"${coin_df['high'].max():,.2f}")
            ck4.metric("Range Low",
                       f"${coin_df['low'].min():,.4f}" if coin_df['low'].min()<1
                       else f"${coin_df['low'].min():,.2f}")
            ck5.metric("Data Since", coin_df["date"].min().strftime("%Y-%m-%d"))

            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

            # ── 4-panel chart: Price / RSI / MACD / Volume ────────────
            fig_coin = make_subplots(
                rows=4, cols=1,
                row_heights=[0.52, 0.18, 0.18, 0.12],
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=["Price", "RSI  ·  30/70 zones", "MACD  ·  histogram", "Volume"],
            )

            # Price panel
            if chart_type == "Line":
                fig_coin.add_trace(go.Scatter(
                    x=coin_df["date"], y=coin_df["close"], mode="lines", name="Close",
                    line=dict(color=ACCENT, width=1.8), fill="tozeroy",
                    fillcolor="rgba(0,245,212,0.06)",
                    hovertemplate="%{x|%Y-%m-%d}<br>Close: $%{y:,.4f}<extra></extra>",
                ), row=1, col=1)
            elif chart_type == "Candlestick":
                fig_coin.add_trace(go.Candlestick(
                    x=coin_df["date"], open=coin_df["open"], high=coin_df["high"],
                    low=coin_df["low"], close=coin_df["close"], name=selected_symbol,
                    increasing_line_color=ACCENT, decreasing_line_color=ACCENT2,
                    increasing_fillcolor="rgba(0,245,212,0.6)",
                    decreasing_fillcolor="rgba(247,37,133,0.6)",
                ), row=1, col=1)
            else:
                fig_coin.add_trace(go.Ohlc(
                    x=coin_df["date"], open=coin_df["open"], high=coin_df["high"],
                    low=coin_df["low"], close=coin_df["close"], name=selected_symbol,
                    increasing_line_color=ACCENT, decreasing_line_color=ACCENT2,
                ), row=1, col=1)

            if chart_type == "Line" and len(coin_df) >= 20:
                coin_df["ma20"] = coin_df["close"].rolling(20).mean()
                fig_coin.add_trace(go.Scatter(
                    x=coin_df["date"], y=coin_df["ma20"], mode="lines", name="20d MA",
                    line=dict(color=GOLD, width=1.2, dash="dot"),
                ), row=1, col=1)

            # RSI panel
            if "RSI" in coin_df.columns:
                fig_coin.add_trace(go.Scatter(
                    x=coin_df["date"], y=coin_df["RSI"], mode="lines", name="RSI",
                    line=dict(color="#7209b7", width=1.5), showlegend=False,
                    hovertemplate="%{x|%Y-%m-%d}<br>RSI: %{y:.1f}<extra></extra>",
                ), row=2, col=1)
                fig_coin.add_hrect(y0=70, y1=100, fillcolor="rgba(255,214,10,0.07)",
                                   line_width=0, row=2, col=1)
                fig_coin.add_hrect(y0=0,  y1=30,  fillcolor="rgba(247,37,133,0.07)",
                                   line_width=0, row=2, col=1)
                fig_coin.add_hline(y=70, line=dict(color=GOLD,   width=0.8, dash="dash"), row=2, col=1)
                fig_coin.add_hline(y=30, line=dict(color=ACCENT2,width=0.8, dash="dash"), row=2, col=1)

            # MACD panel
            if all(c in coin_df.columns for c in ["MACD","MACD_Signal","MACD_Hist"]):
                macd_colors = [ACCENT if v >= 0 else ACCENT2
                               for v in coin_df["MACD_Hist"].fillna(0)]
                fig_coin.add_trace(go.Bar(
                    x=coin_df["date"], y=coin_df["MACD_Hist"], name="MACD Hist",
                    marker=dict(color=macd_colors, opacity=0.7), showlegend=False,
                    hovertemplate="%{x|%Y-%m-%d}<br>Hist: %{y:.4f}<extra></extra>",
                ), row=3, col=1)
                fig_coin.add_trace(go.Scatter(
                    x=coin_df["date"], y=coin_df["MACD"], mode="lines", name="MACD",
                    line=dict(color=ACCENT, width=1.2), showlegend=False,
                ), row=3, col=1)
                fig_coin.add_trace(go.Scatter(
                    x=coin_df["date"], y=coin_df["MACD_Signal"], mode="lines", name="Signal",
                    line=dict(color=GOLD, width=1.0, dash="dot"), showlegend=False,
                ), row=3, col=1)
                fig_coin.add_hline(y=0, line=dict(color=MUTED, width=0.8, dash="dot"), row=3, col=1)

            # Volume panel
            vol_colors = [ACCENT if c>=o else ACCENT2
                          for c,o in zip(coin_df["close"], coin_df["open"])]
            fig_coin.add_trace(go.Bar(
                x=coin_df["date"], y=coin_df["volume_usd"], name="Volume",
                marker=dict(color=vol_colors, opacity=0.55), showlegend=False,
            ), row=4, col=1)

            coin_name_full = coin_df["name"].iloc[0] if "name" in coin_df.columns else selected_symbol
            fig_coin.update_layout(
                **BASE_LAYOUT,
                hovermode   = "x unified", 
                title=title_cfg(f"◈  {selected_symbol}  ·  {coin_name_full}  ·  {date_range}  ·  {chart_type}"),
                height=780, xaxis_rangeslider_visible=False, showlegend=True,
                legend=dict(orientation="h", x=0.01, y=1.02,
                            bgcolor="rgba(0,0,0,0.5)", bordercolor="#1e2d45", borderwidth=1),
            )
            for ann in fig_coin.layout.annotations:
                ann.font.color = MUTED
                ann.font.size  = 11
            fig_coin.update_xaxes(gridcolor="#1a2540", zerolinecolor="#1a2540",
                                   tickfont=dict(color=MUTED, family="JetBrains Mono"))
            fig_coin.update_yaxes(gridcolor="#1a2540", zerolinecolor="#1a2540",
                                   tickfont=dict(color=MUTED, family="JetBrains Mono"))
            st.plotly_chart(fig_coin, width='stretch')

            # ── Regime State Cards ────────────────────────────────────
            st.markdown(
                f"<div style='font-size:13px;color:{ACCENT};margin:12px 0 10px 0;"
                f"text-transform:uppercase;letter-spacing:1px'>"
                f"◈  Current Regime State  ·  {selected_symbol}  ·  latest snapshot</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color:{MUTED};font-size:12px;font-family:JetBrains Mono;"
                f"margin-bottom:14px'>"
                "Each card reads one technical signal independently. "
                "When 4+ signals agree (e.g. all bullish), conviction is high. "
                "Mixed signals suggest a transitional or choppy regime with no clear directional edge. "
                "Use these cards alongside the chart — regime context explains <i>why</i> a pattern is forming, "
                "not just what price is doing."
                "</div>",
                unsafe_allow_html=True,
            )

            latest_row = regime_snapshot[regime_snapshot["coin_id"] == coin_id_sel]

            if not latest_row.empty:
                lr = latest_row.iloc[0]
                rsi_txt, rsi_col  = rsi_label(lr.get("RSI"))
                adx_txt, adx_col  = adx_label(lr.get("ADX"))
                tr_txt,  tr_col   = trend_label(lr.get("Supertrend_Direction"), lr.get("PSAR_Trend"))
                bb_txt,  bb_col   = bb_label(lr.get("BB_Percent"))
                ema_txt, ema_col  = ema_stack_label(lr.get("ema_stack"))
                surge_val = lr.get("surge_score", float("nan"))
                surge_str = f"{surge_val:.2f}" if not pd.isna(surge_val) else "N/A"

                rc1,rc2,rc3,rc4,rc5,rc6 = st.columns(6)
                rc1.metric("RSI Regime", rsi_txt,
                           help="RSI < 30 = oversold (historically higher mean-reversion probability). RSI > 70 = overbought. Neither guarantees a reversal — context matters.")
                rc2.metric("Trend Strength", adx_txt,
                           help="ADX < 20: no clear trend — range-trading strategies work better here. ADX 20–40: developing trend. ADX > 40: strong directional move, trend-following strategies favoured.")
                rc3.metric("Trend Direction", tr_txt,
                           help="Supertrend + PSAR must both agree for a clean directional signal. Mixed = the two indicators disagree — wait for convergence before acting on direction.")
                rc4.metric("BB Position", bb_txt,
                           help="Bollinger Band %B: 0 = price at lower band, 1 = at upper band. Extremes often precede mean-reversion. Mid-band = price in equilibrium, low-conviction zone.")
                rc5.metric("EMA Stack", ema_txt,
                           help="Bull stack = EMA 9 > EMA 21 > EMA 50 — all three aligned upward, a classic momentum confirmation. Bear stack = fully inverted. Mixed = transition in progress.")
                rc6.metric("Surge Score", surge_str,
                           help="Composite momentum/breakout score aggregating multiple signals. Higher values indicate several indicators simultaneously elevated, suggesting stronger short-term directionality.")

            with st.expander("📋  Raw OHLCV + Indicators", expanded=False):
                show_cols = ["date","open","high","low","close","volume_usd",
                             "RSI","MACD","MACD_Signal","ADX","BB_Percent","surge_score"]
                avail = [c for c in show_cols if c in coin_df.columns]
                show_df = coin_df[avail].sort_values("date", ascending=False).reset_index(drop=True)
                st.dataframe(show_df, use_container_width=True, height=350)


# ──────────────────────────────────────────────────────────────
#  TAB 4 │ RETURN SIMILARITY ENGINE
# ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown(
        "<h2 style='font-family:\"Open Sans\",sans-serif;font-size:26px;font-weight:800;"
        "color:#e2e8f0;margin:0 0 4px 0'>"
        "🔗 Return <span style='color:#00f5d4'>Similarity</span></h2>",
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style='background:#111827;border:1px solid #1e2d45;border-radius:10px;
    padding:16px 20px;margin-bottom:20px;font-family:JetBrains Mono,monospace'>
    <div style='color:#00f5d4;font-size:11px;text-transform:uppercase;
    letter-spacing:1px;margin-bottom:8px'>◈ What this engine measures</div>
    <div style='color:#94a3b8;font-size:13px;line-height:1.8'>
    Ranks every coin by <b style='color:#e2e8f0'>Pearson correlation</b> computed on
    <b style='color:#e2e8f0'>daily log returns</b>.
    A high score means the two coins tend to rise and fall <i>together on the same days</i>,
    regardless of their absolute price difference.
    If BTC posts +2% on a Monday and SOL posts +1.8% on the same Monday, that co-movement
    is captured; a coin that simply drifted upward over months without tracking day-to-day
    moves would not score highly here.
    <b style='color:#00f5d4'>Same-Dir %</b> adds a non-parametric check: out of all shared
    trading days, how often did both coins move in the same direction? It catches correlations
    that Pearson might inflate due to a few large outlier moves.
    The <b style='color:#e2e8f0'>rolling 90-day chart</b> is the most actionable view: it reveals
    whether the correlation is structurally stable or regime-dependent. A correlation that collapses
    to zero during bear markets is far less reliable for hedging or pair-trading than one that
    holds consistently across bull and bear cycles.
    </div></div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([2, 1, 1])

    anchor_options = (
        s[s["cap_tier"].isin(selected_tiers)]
        .sort_values("market_cap", ascending=False)
        [["coin_id","symbol","name","cap_tier"]]
        .drop_duplicates("coin_id")
    )
    anchor_labels = [
        f"{row.symbol}  ·  {row.name}  [{row.cap_tier.upper()}]"
        for row in anchor_options.itertuples()
    ]
    anchor_ids = anchor_options["coin_id"].tolist()

    with sc1:
        anchor_label_sel = st.selectbox(
            "Anchor coin", options=anchor_labels, index=0, key="sim_anchor",
            help="Find the top 10 coins most correlated with this one over the selected window.",
        )
        anchor_symbol = anchor_label_sel.split("  ·  ")[0].strip()
        anchor_id     = anchor_ids[anchor_labels.index(anchor_label_sel)]

    with sc2:
        sim_window = st.selectbox(
            "Correlation window", options=["3M","6M","1Y","2Y","3Y","All"], index=2,
            key="sim_window",
            help="Date window over which Pearson correlation is computed. Longer windows are more stable but less sensitive to recent regime shifts.",
        )
        WIN_DAYS = {"3M":90,"6M":180,"1Y":365,"2Y":730,"3Y":1095,"All":9999}
        window_days = WIN_DAYS[sim_window]

    with sc3:
        show_seasonal = st.checkbox(
            "Show seasonal heatmaps", value=True, key="show_seasonal",
            help="Month × Year return heatmaps for anchor + best match. Useful for spotting calendar seasonality patterns.",
        )

    st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)

    with st.spinner(f"Computing correlations for {anchor_symbol} over {sim_window}…"):
        ret_pivot   = build_return_matrix(df, window_days)
        sim_results = compute_similarity(ret_pivot, anchor_id, top_n=10)

    if sim_results.empty:
        st.warning(
            f"⚠️  Not enough overlapping data for **{anchor_symbol}** in the **{sim_window}** window.  \n"
            f"This usually means **{anchor_symbol}** was launched less than {sim_window} ago, "
            f"or too few other coins in the selected tiers have {sim_window} of history.  \n"
            f"👉  Try a **shorter window** (e.g. 3M or 6M) above."
        )
        st.stop()

    all_ids     = [anchor_id] + sim_results["coin_id"].tolist()
    meta        = get_coin_meta(s, all_ids)
    anchor_meta = meta.get(anchor_id, {"symbol": anchor_symbol, "name": "", "cap_tier": "—"})

    sim_results["symbol"]   = sim_results["coin_id"].map(lambda x: meta.get(x, {}).get("symbol", x))
    sim_results["name"]     = sim_results["coin_id"].map(lambda x: meta.get(x, {}).get("name", ""))
    sim_results["cap_tier"] = sim_results["coin_id"].map(lambda x: meta.get(x, {}).get("cap_tier", "—"))

    sim_results = sim_results[sim_results["cap_tier"].isin(selected_tiers)].reset_index(drop=True)
    sim_results.index += 1

    if sim_results.empty:
        st.warning(f"No similar coins found within the selected cap tiers for {anchor_symbol}.")
        st.stop()

    best_match     = sim_results.iloc[0]
    avg_corr_top10 = sim_results["correlation"].mean()
    avg_dir_top10  = sim_results["pct_same_dir"].mean()
    n_sig          = (sim_results["p_value"] < 0.05).sum()

    sk1, sk2, sk3, sk4 = st.columns(4)
    sk1.metric("Best Match",           best_match["symbol"],
               delta=f"r = {best_match['correlation']:.3f}",
               help="The single coin most correlated with the anchor over the selected window.")
    sk2.metric("Avg Top-10 Corr",      f"{avg_corr_top10:.3f}",
               help="Mean Pearson r across all 10 similar coins. Values above 0.7 indicate a tightly correlated cluster.")
    sk3.metric("Avg Same-Dir %",        f"{avg_dir_top10:.1f}%",
               help="Average share of days where both anchor and peer moved in the same direction. 50% = random, 100% = perfect directional agreement.")
    sk4.metric("Significant (p<0.05)", f"{n_sig} / 10",
               help="Number of the top 10 correlations that are statistically significant at the 5% level. Low count = treat correlations with caution.")

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Correlation bar chart ─────────────────────────────────
    fig_bar = go.Figure()

    bar_y     = sim_results["symbol"].tolist()[::-1]
    bar_x     = sim_results["correlation"].tolist()[::-1]
    bar_dir   = sim_results["pct_same_dir"].tolist()[::-1]
    bar_tiers = sim_results["cap_tier"].tolist()[::-1]
    bar_names = sim_results["name"].tolist()[::-1]
    bar_pval  = sim_results["p_value"].tolist()[::-1]
    bar_nobs  = sim_results["n_obs"].tolist()[::-1]

    fig_bar.add_trace(go.Bar(
        x=bar_x, y=bar_y, orientation="h",
        marker=dict(
            color=bar_x,
            colorscale=[[0.0,"#3a0ca3"],[0.5,"#4361ee"],[0.85,"#00f5d4"],[1.0,"#ffd60a"]],
            cmin=0.0, cmax=1.0, showscale=True,
            colorbar=dict(
                title=dict(text="Pearson r", font=dict(color=MUTED, size=11)),
                tickfont=dict(color=MUTED, family="JetBrains Mono"),
                thickness=12, len=0.6,
            ),
            line=dict(width=0),
        ),
        customdata=list(zip(bar_names, bar_tiers, bar_dir, bar_pval, bar_nobs)),
        hovertemplate=(
            "<b>%{y}</b>  ·  %{customdata[0]}<br>"
            "Tier        : %{customdata[1]}<br>"
            "Pearson r   : %{x:.4f}<br>"
            "Same-dir %  : %{customdata[2]:.1f}%<br>"
            "p-value     : %{customdata[3]:.4f}<br>"
            "Shared obs  : %{customdata[4]}<extra></extra>"
        ),
        text=[f"r={v:.3f}" for v in bar_x],
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
    ))

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
        title=title_cfg(f"◈  Top-10 Most Correlated with {anchor_symbol}  ·  {sim_window} Window"),
        height=420,
        xaxis=dict(title=dict(text="Pearson Correlation (r)", font=dict(color=MUTED)),
                   range=[0, 1.12], **AXIS),
        yaxis=axis_tf(color=TEXT, size=12),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, width='stretch')

    st.markdown("---")

    # ── Normalized price overlay ──────────────────────────────
    st.markdown(
        f"<div style='font-size:13px;color:{ACCENT};margin-bottom:6px'>"
        f"◈  Normalized Price Overlay  ·  rebased to 100  ·  {sim_window} window</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:{MUTED};font-size:12px;font-family:JetBrains Mono;margin-bottom:12px'>"
        "All coins are rebased to 100 at the start of the window. This removes price-scale differences "
        "and lets you see whether the coins tracked each other visually — a high Pearson r should "
        "produce overlapping lines here. Divergences reveal where the correlation broke down."
        "</div>",
        unsafe_allow_html=True,
    )

    top_n_overlay = st.slider(
        "Coins to overlay", min_value=1, max_value=10, value=5, step=1, key="overlay_n",
        help="How many of the top similar coins to show alongside the anchor.",
    )

    overlay_ids  = [anchor_id] + sim_results["coin_id"].head(top_n_overlay).tolist()
    overlay_syms = {cid: meta.get(cid, {}).get("symbol", cid) for cid in overlay_ids}
    rebased      = rebase_prices(close_pivot, overlay_ids)

    fig_ov = go.Figure()

    for i, cid in enumerate(overlay_ids):
        if rebased.empty or cid not in rebased.columns:
            continue
        sym       = overlay_syms[cid]
        is_anchor = (cid == anchor_id)
        color     = GOLD if is_anchor else OVERLAY_PALETTE[i % len(OVERLAY_PALETTE)]
        width     = 2.4 if is_anchor else 1.4
        opacity   = 1.0 if is_anchor else 0.75
        corr_val  = ""
        if not is_anchor:
            row_match = sim_results[sim_results["coin_id"] == cid]
            if not row_match.empty:
                corr_val = f"  r={row_match.iloc[0]['correlation']:.3f}"

        fig_ov.add_trace(go.Scatter(
            x=rebased.index, y=rebased[cid], mode="lines",
            name=f"{'★ ' if is_anchor else ''}{sym}{corr_val}",
            line=dict(color=color, width=width), opacity=opacity,
            hovertemplate=f"{sym}<br>%{{x|%Y-%m-%d}}<br>Indexed: %{{y:.1f}}<extra></extra>",
        ))

    fig_ov.add_hline(y=100, line=dict(color=MUTED, width=1, dash="dot"))
    fig_ov.update_layout(
        **BASE_LAYOUT,
        title=title_cfg(f"◈  Price Pattern Overlap  ·  {anchor_symbol} + Top-{top_n_overlay}  ·  {sim_window}"),
        height=500, showlegend=True,
        legend=dict(orientation="v", x=0.01, y=0.99,
                    bgcolor="rgba(0,0,0,0.65)", bordercolor="#1e2d45", borderwidth=1,
                    font=dict(size=11, family="JetBrains Mono")),
        xaxis=dict(**AXIS, title=dict(text="Date", font=dict(color=MUTED))),
        yaxis=dict(**AXIS, title=dict(text="Indexed Price (base = 100)", font=dict(color=MUTED))),
    )
    st.plotly_chart(fig_ov, width='stretch')

    st.markdown("---")

    # ── Rolling correlation ───────────────────────────────────
    st.markdown(
        f"<div style='font-size:13px;color:{ACCENT};margin-bottom:6px'>"
        f"◈  Rolling 90-Day Correlation  ·  {anchor_symbol} vs Top-5 Matches</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:{MUTED};font-size:12px;font-family:JetBrains Mono;margin-bottom:12px'>"
        "The overall Pearson r (shown in the bar chart above) is a single number that averages "
        "across the entire window. This rolling chart reveals the <i>dynamics</i> beneath that average. "
        "A line that drops sharply during a market crash means the correlation was regime-dependent — "
        "the pair only moved together during benign conditions. "
        "Stable lines near 0.8+ indicate a structural relationship worth trading."
        "</div>",
        unsafe_allow_html=True,
    )

    top5_ids  = sim_results["coin_id"].head(5).tolist()
    top5_syms = {cid: meta.get(cid, {}).get("symbol", cid) for cid in top5_ids}
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
            x=rolling_corr.index, y=rolling_corr.values, mode="lines",
            name=sym, line=dict(color=color, width=1.6),
            hovertemplate=f"{anchor_symbol}↔{sym}<br>%{{x|%Y-%m-%d}}<br>90d Corr: %{{y:.3f}}<extra></extra>",
        ))

    fig_roll.add_hline(y=0,   line=dict(color=MUTED, width=1, dash="dot"))
    fig_roll.add_hline(y=0.7, line=dict(color=GOLD,  width=0.8, dash="dash"),
                       annotation_text="r=0.7", annotation_font=dict(color=GOLD, size=10),
                       annotation_position="right")
    fig_roll.update_layout(
        **BASE_LAYOUT,
        title=title_cfg(f"◈  Rolling 90d Correlation  ·  {anchor_symbol} vs Top-5  ·  Regime Changes Visible"),
        height=420, showlegend=True,
        legend=dict(orientation="h", x=0.01, y=1.02,
                    bgcolor="rgba(0,0,0,0.6)", bordercolor="#1e2d45", borderwidth=1,
                    font=dict(size=11, family="JetBrains Mono")),
        xaxis=dict(**AXIS, title=dict(text="Date", font=dict(color=MUTED))),
        yaxis=dict(**AXIS, title=dict(text="Pearson r  (90d rolling)", font=dict(color=MUTED)),
                   range=[-1.1, 1.1]),
    )
    st.plotly_chart(fig_roll, width='stretch')

    # ── Seasonal heatmaps ─────────────────────────────────────
    if show_seasonal:
        st.markdown("---")
        st.markdown(
            f"<div style='font-size:13px;color:{ACCENT};margin-bottom:6px'>"
            f"◈  Seasonal Return Heatmap  ·  Month × Year  ·  "
            f"{anchor_symbol}  vs  {best_match['symbol']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='color:{MUTED};font-size:12px;font-family:JetBrains Mono;margin-bottom:12px'>"
            "Each cell shows the total return for that calendar month in that year. "
            "Teal cells = positive month, red = negative. Reading across a row (e.g. January) "
            "reveals whether the coin has a consistent seasonal bias in that month. "
            "If both coins show the same red/teal pattern, their seasonal behaviour is aligned — "
            "consistent with a high return correlation."
            "</div>",
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
                z=z_vals, x=x_vals, y=y_vals,
                colorscale=[[0.0,"#f72585"],[0.35,"#3a0ca3"],[0.5,"#1e2d45"],[0.65,"#4361ee"],[1.0,"#00f5d4"]],
                zmid=0,
                text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z_vals],
                texttemplate="%{text}",
                textfont=dict(size=10, family="JetBrains Mono", color="white"),
                hovertemplate="%{y} %{x}<br>Return: %{z:.1f}%<extra></extra>",
                showscale=True,
                colorbar=dict(
                    title=dict(text="Ret %", font=dict(color=MUTED, size=10)),
                    tickfont=dict(color=MUTED, family="JetBrains Mono", size=10),
                    thickness=10, len=0.8,
                ),
            ))
            fig_s.update_layout(
                paper_bgcolor=BG, plot_bgcolor=GRID,
                title=title_cfg(title_h, size=14), height=400,
                margin=dict(t=50, b=30, l=60, r=40),
                font=dict(family="JetBrains Mono", color=TEXT, size=11),
                xaxis=dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540"),
                yaxis=dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540", autorange="reversed"),
            )
            return fig_s

        with sh_col1:
            fig_s_anchor = render_seasonal_heatmap(anchor_id, f"◈  {anchor_symbol}  ·  Monthly Returns")
            if fig_s_anchor:
                st.plotly_chart(fig_s_anchor, width='stretch')
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
                st.plotly_chart(fig_s_best, width='stretch')
            else:
                st.info(f"No seasonal data for {best_sym}.")

        st.markdown(
            f"<div style='font-size:12px;color:{MUTED};margin-top:8px;margin-bottom:8px'>"
            f"◈  Δ Return Heatmap  ·  {anchor_symbol}  −  {best_sym}  "
            f"(teal = anchor outperformed, red = anchor underperformed)</div>",
            unsafe_allow_html=True,
        )

        seas_a = seasonal_monthly_returns(df_pd, anchor_id)
        seas_b = seasonal_monthly_returns(df_pd, best_cid)
        if not seas_a.empty and not seas_b.empty:
            common_years = seas_a.columns.intersection(seas_b.columns)
            diff_hm = seas_a[common_years] - seas_b[common_years]
            fig_diff = go.Figure(go.Heatmap(
                z=diff_hm.values,
                x=[str(c) for c in common_years],
                y=diff_hm.index.tolist(),
                colorscale=[[0.0,"#f72585"],[0.5,"#1e2d45"],[1.0,"#00f5d4"]],
                zmid=0,
                text=[[f"{v:+.1f}%" if not np.isnan(v) else "" for v in row] for row in diff_hm.values],
                texttemplate="%{text}",
                textfont=dict(size=10, family="JetBrains Mono", color="white"),
                hovertemplate="%{y} %{x}<br>Δ: %{z:.1f}%<extra></extra>",
                showscale=True,
                colorbar=dict(
                    title=dict(text="Δ Ret %", font=dict(color=MUTED, size=10)),
                    tickfont=dict(color=MUTED, family="JetBrains Mono", size=10),
                    thickness=10,
                ),
            ))
            fig_diff.update_layout(
                paper_bgcolor=BG, plot_bgcolor=GRID,
                title=title_cfg(f"◈  Δ Return  ·  {anchor_symbol} − {best_sym}  ·  Month × Year", size=14),
                height=400, margin=dict(t=50, b=30, l=60, r=40),
                font=dict(family="JetBrains Mono", color=TEXT, size=11),
                xaxis=dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540"),
                yaxis=dict(tickfont=dict(color=MUTED, size=11), gridcolor="#1a2540", autorange="reversed"),
            )
            st.plotly_chart(fig_diff, width='stretch')

    # ── Full similarity table ─────────────────────────────────
    st.markdown("---")
    with st.expander(
        f"📋  Full Similarity Table  ·  {anchor_symbol}  ·  Top-10  ·  {sim_window} window",
        expanded=True,
    ):
        disp_sim = sim_results[["symbol","name","cap_tier","correlation","p_value","n_obs","pct_same_dir"]].copy()
        disp_sim.columns = ["Symbol","Name","Tier","Pearson r","p-value","Obs","Same-Dir %"]
        styled_sim = (
            disp_sim.style
            .background_gradient(subset=["Pearson r"],   cmap="RdYlGn", vmin=0, vmax=1)
            .background_gradient(subset=["Same-Dir %"], cmap="Blues",  vmin=50, vmax=100)
            .set_properties(
                subset=["Pearson r"],
                **{"font-weight":"bold","border-left":"2px solid #ffd60a","border-right":"2px solid #ffd60a"},
            )
            .format({"Pearson r":"{:.4f}","p-value":"{:.4f}","Same-Dir %":"{:.1f}%"})
        )
        st.dataframe(styled_sim, use_container_width=True, height=360)


# ──────────────────────────────────────────────────────────────
#  TAB 5 │ REGIME SIMILARITY
# ──────────────────────────────────────────────────────────────
with tab5:
    st.markdown(
        "<h2 style='font-family:\"Open Sans\",sans-serif;font-size:26px;font-weight:800;"
        "color:#e2e8f0;margin:0 0 4px 0'>"
        "🧭 Regime <span style='color:#00f5d4'>Similarity</span></h2>",
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style='background:#111827;border:1px solid #1e2d45;border-radius:10px;
    padding:16px 20px;margin-bottom:20px;font-family:JetBrains Mono,monospace'>
    <div style='color:#00f5d4;font-size:11px;text-transform:uppercase;
    letter-spacing:1px;margin-bottom:8px'>◈ How regime similarity differs from return similarity</div>
    <div style='color:#94a3b8;font-size:13px;line-height:1.8'>
    Return similarity (Tab 4) asks: <i>"which coins moved together historically?"</i> —
    it is backward-looking across a chosen window. Regime similarity asks:
    <i>"which coins are in the same technical state <b style='color:#e2e8f0'>right now</b>?"</i>
    — it is a snapshot of today's indicator readings.<br><br>
    We build an <b style='color:#e2e8f0'>11-feature technical vector</b> for each coin's latest row:
    RSI, Bollinger Band %, ADX, +DI/−DI, Supertrend direction, Parabolic SAR, CMF, MFI,
    Aroon Oscillator, and EMA stack alignment (9/21/50).
    Each feature is <b style='color:#e2e8f0'>z-score normalised</b> across the entire coin universe
    so that scale-dependent indicators do not dominate scale-independent ones.
    We then compute <b style='color:#e2e8f0'>cosine similarity</b> between the anchor's vector
    and every other coin's vector. A cosine score near 1.0 means both coins are technically
    co-positioned today — same momentum zone, same trend regime, same band position.<br><br>
    <b style='color:#00f5d4'>Practical uses:</b> pair-trading setups (two coins in the same regime
    that historically diverge), portfolio diversification (avoid two holdings with identical
    regime vectors — they will react identically to macro shocks), and sector rotation
    (coins leaving one regime cluster and entering another are in transition).
    </div></div>
    """, unsafe_allow_html=True)

    rs1, rs2 = st.columns([2, 1])

    regime_anchor_options = (
        s[s["cap_tier"].isin(selected_tiers)]
        .sort_values("market_cap", ascending=False)
        [["coin_id","symbol","name","cap_tier"]]
        .drop_duplicates("coin_id")
    )
    regime_anchor_labels = [
        f"{r.symbol}  ·  {r.name}  [{r.cap_tier.upper()}]"
        for r in regime_anchor_options.itertuples()
    ]
    regime_anchor_ids = regime_anchor_options["coin_id"].tolist()

    with rs1:
        reg_anchor_sel = st.selectbox(
            "Anchor coin", options=regime_anchor_labels, index=0, key="reg_anchor",
            help="Find coins in the most similar technical regime to this one right now.",
        )
        reg_anchor_id  = regime_anchor_ids[regime_anchor_labels.index(reg_anchor_sel)]
        reg_anchor_sym = reg_anchor_sel.split("  ·  ")[0].strip()

    with rs2:
        reg_top_n = st.slider(
            "Top N similar", min_value=3, max_value=10, value=8, step=1, key="reg_top_n",
        )

    with st.spinner(f"Computing regime similarity for {reg_anchor_sym}…"):
        reg_sim, anchor_raw = compute_regime_similarity(
            regime_snapshot, reg_anchor_id, selected_tiers, top_n=reg_top_n
        )

    if reg_sim.empty:
        st.warning(
            f"⚠️  Not enough indicator data for **{reg_anchor_sym}** in the selected tiers.  \n"
            "Try including more cap tiers in the sidebar."
        )
        st.stop()

    # ── Anchor regime state cards ─────────────────────────────
    st.markdown(
        f"<div style='font-size:12px;color:{MUTED};margin:8px 0 12px 0'>"
        f"◈  Anchor regime state  ·  {reg_anchor_sym}  ·  latest snapshot</div>",
        unsafe_allow_html=True,
    )

    if not anchor_raw.empty:
        ar = anchor_raw.iloc[0]
        ac1,ac2,ac3,ac4,ac5,ac6 = st.columns(6)
        rsi_t, rsi_c = rsi_label(ar.get("RSI"))
        adx_t, adx_c = adx_label(ar.get("ADX"))
        tr_t,  tr_c  = trend_label(ar.get("Supertrend_Direction"), ar.get("PSAR_Trend"))
        bb_t,  bb_c  = bb_label(ar.get("BB_Percent"))
        ema_t, ema_c = ema_stack_label(ar.get("ema_stack"))

        ac1.metric("RSI",         f"{ar.get('RSI', float('nan')):.1f}",
                   delta=rsi_t, help="Momentum oscillator 0–100. Used as the primary overbought/oversold signal in the feature vector.")
        ac2.metric("ADX",         f"{ar.get('ADX', float('nan')):.1f}",
                   delta=adx_t, help="Trend strength. < 20 = ranging market. > 40 = strong trend. Does not indicate direction.")
        ac3.metric("Trend",       tr_t,
                   help="Combined Supertrend + PSAR signal. Both must agree for a clean directional read.")
        ac4.metric("BB Position", f"{ar.get('BB_Percent', float('nan')):.2f}",
                   delta=bb_t, help="0 = price at lower Bollinger Band, 1 = upper band. Mid = ~0.5.")
        ac5.metric("EMA Stack",   ema_t,
                   help="EMA 9/21/50 alignment. Bull stack = all ascending. Bear stack = all descending.")
        ac6.metric("Surge Score", f"{ar.get('surge_score', float('nan')):.2f}",
                   help="Composite momentum/breakout score. Included in the regime vector as a summary signal.")

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    # ── Cosine similarity bar chart ───────────────────────────
    fig_reg = go.Figure()

    reg_y     = reg_sim["symbol"].tolist()[::-1]
    reg_x     = reg_sim["cosine_sim"].tolist()[::-1]
    reg_tiers = reg_sim["cap_tier"].tolist()[::-1]
    reg_names = reg_sim["name"].tolist()[::-1]
    reg_rsi   = reg_sim["RSI"].tolist()[::-1]
    reg_adx   = reg_sim["ADX"].tolist()[::-1]
    reg_surge = reg_sim["surge_score"].tolist()[::-1]

    fig_reg.add_trace(go.Bar(
        x=reg_x, y=reg_y, orientation="h",
        marker=dict(
            color=reg_x,
            colorscale=[[0,"#3a0ca3"],[0.5,"#4361ee"],[0.85,"#00f5d4"],[1.0,"#ffd60a"]],
            cmin=0, cmax=1, showscale=True,
            colorbar=dict(
                title=dict(text="Cosine", font=dict(color=MUTED, size=11)),
                tickfont=dict(color=MUTED, family="JetBrains Mono"),
                thickness=12, len=0.6,
            ),
            line=dict(width=0),
        ),
        customdata=list(zip(reg_names, reg_tiers, reg_rsi, reg_adx, reg_surge)),
        hovertemplate=(
            "<b>%{y}</b>  ·  %{customdata[0]}<br>"
            "Tier         : %{customdata[1]}<br>"
            "Cosine Sim   : %{x:.4f}<br>"
            "RSI          : %{customdata[2]:.1f}<br>"
            "ADX          : %{customdata[3]:.1f}<br>"
            "Surge Score  : %{customdata[4]:.2f}<extra></extra>"
        ),
        text=[f"{v:.3f}" for v in reg_x],
        textposition="outside",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
    ))

    fig_reg.update_layout(
        **BASE_LAYOUT,
        title=title_cfg(f"◈  Top-{reg_top_n} Regime-Similar to {reg_anchor_sym}  ·  Cosine Similarity on 11 Indicators"),
        height=420,
        xaxis=dict(title=dict(text="Cosine Similarity", font=dict(color=MUTED)),
                   range=[0, 1.15], **AXIS),
        yaxis=axis_tf(color=TEXT, size=12),
        showlegend=False,
    )
    st.plotly_chart(fig_reg, width='stretch')

    # ── Feature radar ─────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f"<div style='font-size:13px;color:{ACCENT};margin-bottom:6px'>"
        f"◈  Feature Radar  ·  {reg_anchor_sym}  vs  Best Regime Match</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='color:{MUTED};font-size:12px;font-family:JetBrains Mono;margin-bottom:14px'>"
        "Each spoke represents one technical feature, normalised 0→1 within the universe. "
        "Overlapping filled shapes = technically co-positioned coins. "
        "Spokes that diverge reveal exactly <i>which</i> indicators differ despite an overall high cosine score — "
        "for example, two coins may share RSI and ADX levels but diverge on CMF (money flow), "
        "suggesting one has stronger institutional buying behind its move."
        "</div>",
        unsafe_allow_html=True,
    )

    best_reg_row = reg_sim.iloc[0]
    best_reg_sym = best_reg_row["symbol"]

    radar_feats  = ["RSI","BB_Percent","ADX","PLUS_DI","MINUS_DI","CMF","MFI","Aroon_Oscillator"]
    radar_labels = [REGIME_FEATURE_LABELS.get(f, f) for f in radar_feats]

    def normalise_val(val, col, df):
        mn, mx = df[col].min(), df[col].max()
        return (val - mn) / (mx - mn) if mx > mn else 0.5

    fig_radar = go.Figure()

    for cid, sym, color in [
        (reg_anchor_id,            reg_anchor_sym,  GOLD),
        (best_reg_row["coin_id"],  best_reg_sym,    ACCENT),
    ]:
        row_data = regime_snapshot[regime_snapshot["coin_id"] == cid]
        if row_data.empty:
            continue
        row  = row_data.iloc[0]
        vals = [normalise_val(row.get(f, 0), f, regime_snapshot) for f in radar_feats]
        vals += [vals[0]]

        fill_color = f"rgba(255,214,10,0.12)" if color == GOLD else f"rgba(0,245,212,0.12)"
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=radar_labels + [radar_labels[0]],
            fill="toself", name=sym,
            line=dict(color=color, width=2),
            fillcolor=fill_color,
        ))

    fig_radar.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        polar=dict(
            bgcolor=GRID,
            radialaxis=dict(visible=True, range=[0,1],
                            tickfont=dict(color=MUTED, size=9), gridcolor="#1a2540"),
            angularaxis=dict(tickfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
                             gridcolor="#1a2540"),
        ),
        font=dict(family="JetBrains Mono", color=TEXT),
        legend=dict(bgcolor="rgba(0,0,0,0.6)", bordercolor="#1e2d45", borderwidth=1,
                    font=dict(size=12)),
        height=440,
        title=title_cfg(
            f"◈  Regime Radar  ·  {reg_anchor_sym}  vs  {best_reg_sym}"
            f"  (cosine={best_reg_row['cosine_sim']:.3f})"
        ),
        margin=dict(t=60, b=30, l=60, r=60),
    )
    st.plotly_chart(fig_radar, width='stretch')

    # ── Full regime table ─────────────────────────────────────
    st.markdown("---")
    with st.expander(
        f"📋  Full Regime Table  ·  {reg_anchor_sym}  ·  Top-{reg_top_n}",
        expanded=True,
    ):
        disp_reg = reg_sim[[
            "symbol","name","cap_tier","cosine_sim",
            "RSI","ADX","BB_Percent","Aroon_Oscillator","surge_score",
        ]].copy()
        disp_reg.columns = ["Symbol","Name","Tier","Cosine Sim","RSI","ADX","BB%","Aroon Osc","Surge Score"]
        styled_reg = (
            disp_reg.style
            .background_gradient(subset=["Cosine Sim"], cmap="YlGn",   vmin=0, vmax=1)
            .background_gradient(subset=["RSI"],        cmap="RdYlGn", vmin=0, vmax=100)
            .background_gradient(subset=["ADX"],        cmap="Blues",  vmin=0, vmax=60)
            .format({
                "Cosine Sim":"{:.4f}","RSI":"{:.1f}","ADX":"{:.1f}",
                "BB%":"{:.2f}","Aroon Osc":"{:.1f}","Surge Score":"{:.2f}",
            }, na_rep="—")
        )
        st.dataframe(styled_reg, use_container_width=True, height=360)


# ──────────────────────────────────────────────────────────────
#  TAB 6 │ FORWARD RETURN LAB
# ──────────────────────────────────────────────────────────────
with tab6:
    st.markdown(
        "<h2 style='font-family:\"Open Sans\",sans-serif;font-size:26px;font-weight:800;"
        "color:#e2e8f0;margin:0 0 4px 0'>"
        "🔮 Forward Return <span style='color:#00f5d4'>Lab</span></h2>",
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div style='background:#111827;border:1px solid #1e2d45;border-radius:10px;
    padding:16px 20px;margin-bottom:20px;font-family:JetBrains Mono,monospace'>
    <div style='color:#00f5d4;font-size:11px;text-transform:uppercase;
    letter-spacing:1px;margin-bottom:8px'>◈ What this lab answers</div>
    <div style='color:#94a3b8;font-size:13px;line-height:1.8'>
    This tab uses the dataset's pre-computed
    <b style='color:#e2e8f0'>Next_1d / 2d / 3d / 5d / 7d_Return</b> columns —
    the actual subsequent returns already labelled in the data — to ask a conditional question:<br><br>
    <i>"Historically, when this coin was in a similar RSI + ADX regime to today,
    what did its returns look like over the next 1 to 7 days?"</i><br><br>
    This is <b style='color:#e2e8f0'>not a prediction</b>. It is a
    <b style='color:#e2e8f0'>historical base-rate analysis</b> — the same logic
    a sports analyst uses when saying "teams leading at half-time win 72% of the time."
    Knowing the base rate does not guarantee the next outcome, but it shifts your prior.
    If the coin has been in a similar RSI+ADX regime 40 times historically and the
    median 5-day return was +4%, that is useful context for position sizing, even if
    individual instances vary widely.<br><br>
    The <b style='color:#00f5d4'>Surge Score scatter</b> adds a second test:
    within this matched regime, do coins with higher surge scores actually go on to post
    higher 5-day returns? If the OLS trend line slopes upward and the r value is
    meaningful, surge score has incremental predictive value here — if the line is flat,
    it does not. The data tells you which regime-coin combinations respond to momentum
    signals and which do not.
    </div></div>
    """, unsafe_allow_html=True)

    fl1, fl2, fl3 = st.columns([2, 1, 1])

    fwd_coin_options = (
        s[s["cap_tier"].isin(selected_tiers)]
        .sort_values("market_cap", ascending=False)
        [["coin_id","symbol","name","cap_tier"]]
        .drop_duplicates("coin_id")
    )
    fwd_labels = [
        f"{r.symbol}  ·  {r.name}  [{r.cap_tier.upper()}]"
        for r in fwd_coin_options.itertuples()
    ]
    fwd_ids = fwd_coin_options["coin_id"].tolist()

    with fl1:
        fwd_sel = st.selectbox("Coin", options=fwd_labels, index=0, key="fwd_coin")
        fwd_id  = fwd_ids[fwd_labels.index(fwd_sel)]
        fwd_sym = fwd_sel.split("  ·  ")[0].strip()
    with fl2:
        rsi_tol = st.slider("RSI tolerance ±", 5, 20, 10, key="rsi_tol",
                            help="Match historical dates where RSI was within ± this band of today's RSI. Tighter = fewer matches, more precise. Wider = more matches, noisier.")
    with fl3:
        adx_tol = st.slider("ADX tolerance ±", 5, 20, 10, key="adx_tol",
                            help="Match historical dates where ADX was within ± this band of today's ADX. ADX is slower-moving — a tighter band (±5) is often sufficient.")

    fwd_snap = regime_snapshot[regime_snapshot["coin_id"] == fwd_id]

    if fwd_snap.empty:
        st.warning(f"No regime snapshot available for {fwd_sym}.")
        st.stop()

    anchor_rsi   = fwd_snap.iloc[0].get("RSI",   50.0)
    anchor_adx   = fwd_snap.iloc[0].get("ADX",   25.0)
    anchor_surge = fwd_snap.iloc[0].get("surge_score", float("nan"))

    st.markdown(
        f"<div style='font-size:12px;color:{MUTED};margin:8px 0 16px 0;font-family:JetBrains Mono'>"
        f"Current RSI: <b style='color:{ACCENT}'>{anchor_rsi:.1f}</b>  ·  "
        f"Current ADX: <b style='color:{ACCENT}'>{anchor_adx:.1f}</b>  ·  "
        f"Surge Score: <b style='color:{GOLD}'>{anchor_surge:.2f}</b>  ·  "
        f"Searching for RSI ∈ [{anchor_rsi-rsi_tol:.0f}, {anchor_rsi+rsi_tol:.0f}]  "
        f"ADX ∈ [{anchor_adx-adx_tol:.0f}, {anchor_adx+adx_tol:.0f}]"
        f"</div>",
        unsafe_allow_html=True,
    )

    similar_hist = forward_return_in_regime(
        df_pd, fwd_id,
        anchor_rsi=anchor_rsi, anchor_adx=anchor_adx,
        rsi_tol=float(rsi_tol), adx_tol=float(adx_tol),
    )

    if similar_hist.empty or len(similar_hist) < 5:
        st.warning(
            f"⚠️  Only {len(similar_hist)} historical matches for {fwd_sym} "
            f"in the RSI±{rsi_tol} / ADX±{adx_tol} bands.  \n"
            "Try widening the tolerance sliders above — at least 15–20 matches are needed for reliable base rates."
        )
    else:
        fk1, fk2, fk3, fk4 = st.columns(4)
        fk1.metric("Matched Dates",  f"{len(similar_hist)}",
                   help="Number of historical days where RSI and ADX were in the same regime band as today. More matches = more reliable distribution.")
        fk2.metric("Median 1d Fwd",  f"{similar_hist['Next_1d_Return'].median()*100:.2f}%",
                   delta=f"{'+' if similar_hist['Next_1d_Return'].median()>0 else ''}{similar_hist['Next_1d_Return'].median()*100:.2f}%",
                   help="Median next-day return across all matched instances. The median is preferred over the mean here because crypto returns are heavily skewed by outlier days.")
        fk3.metric("Median 5d Fwd",  f"{similar_hist['Next_5d_Return'].median()*100:.2f}%",
                   delta=f"{'+' if similar_hist['Next_5d_Return'].median()>0 else ''}{similar_hist['Next_5d_Return'].median()*100:.2f}%",
                   help="Median 5-day forward return. The 5-day horizon is often the most actionable for short-term discretionary trades.")
        fk4.metric("% Positive 5d",  f"{(similar_hist['Next_5d_Return']>0).mean()*100:.0f}%",
                   help="Share of matched instances where the 5-day return was positive. > 60% is a meaningful bullish skew. < 40% is meaningfully bearish.")

        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

        # ── Box plot ──────────────────────────────────────────
        st.markdown(
            f"<div style='font-size:13px;color:{ACCENT};margin-bottom:6px'>"
            f"◈  Forward Return Distribution  ·  {len(similar_hist)} matched dates  ·  {fwd_sym}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='color:{MUTED};font-size:12px;font-family:JetBrains Mono;margin-bottom:12px'>"
            "Each box covers the interquartile range (25th–75th percentile) of forward returns "
            "across all matched historical dates. The centre line is the median. "
            "Whiskers extend to the 5th and 95th percentiles — points beyond are outliers. "
            "A box that sits entirely above zero at the 1d horizon and grows at 5d and 7d "
            "suggests momentum continuation in this regime. "
            "A box crossing zero means the regime has historically been inconclusive — "
            "position sizing should reflect that uncertainty."
            "</div>",
            unsafe_allow_html=True,
        )

        ret_cols   = ["Next_1d_Return","Next_2d_Return","Next_3d_Return","Next_5d_Return","Next_7d_Return"]
        ret_labels = ["1d","2d","3d","5d","7d"]
        ret_cols   = [c for c in ret_cols if c in similar_hist.columns]

        fig_box = go.Figure()
        for col, lbl in zip(ret_cols, ret_labels):
            vals  = similar_hist[col].dropna() * 100
            color = ACCENT if vals.median() >= 0 else ACCENT2
            fig_box.add_trace(go.Box(
                y=vals, name=lbl,
                marker=dict(color=color, opacity=0.8),
                line=dict(color=color), boxmean=True,
                hovertemplate=f"Horizon: {lbl}<br>Return: %{{y:.2f}}%<extra></extra>",
            ))

        fig_box.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dot"))
        fig_box.update_layout(
            **BASE_LAYOUT,
            title=title_cfg(
                f"◈  {fwd_sym}  ·  Forward Return Distributions  ·  RSI±{rsi_tol} / ADX±{adx_tol}  ·  n={len(similar_hist)}"
            ),
            height=440,
            xaxis=dict(**AXIS, title=dict(text="Horizon", font=dict(color=MUTED))),
            yaxis=dict(**AXIS, title=dict(text="Return %", font=dict(color=MUTED))),
            showlegend=False,
        )
        st.plotly_chart(fig_box, width='stretch')

        # ── Surge score scatter ───────────────────────────────
        if "surge_score" in similar_hist.columns and "Next_5d_Return" in similar_hist.columns:
            st.markdown("---")
            st.markdown(
                f"<div style='font-size:13px;color:{ACCENT};margin-bottom:6px'>"
                f"◈  Surge Score vs 5d Forward Return  ·  {fwd_sym}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color:{MUTED};font-size:12px;font-family:JetBrains Mono;margin-bottom:12px'>"
                "Each point is one matched historical date. The x-axis is the surge score on that date; "
                "the y-axis is the 5-day return that followed. "
                "If surge score carries signal within this regime, higher surge days should cluster "
                "toward higher returns — visible as an upward-sloping OLS line. "
                "The <b style='color:#e2e8f0'>r value</b> on the trend line measures linear association: "
                "r > 0.3 is worth noting; r > 0.5 is strong for a single indicator. "
                "A flat or negative slope means surge score is not informative for this coin in this regime "
                "— check other indicators in the Regime Similarity tab instead."
                "</div>",
                unsafe_allow_html=True,
            )

            scatter_df = similar_hist[["date","surge_score","Next_5d_Return"]].dropna()
            scatter_df["ret_5d_pct"] = scatter_df["Next_5d_Return"] * 100
            dot_colors = [ACCENT if v >= 0 else ACCENT2 for v in scatter_df["ret_5d_pct"]]

            fig_sc = go.Figure()
            fig_sc.add_trace(go.Scatter(
                x=scatter_df["surge_score"], y=scatter_df["ret_5d_pct"],
                mode="markers",
                marker=dict(color=dot_colors, size=7, opacity=0.75,
                            line=dict(width=0.5, color="rgba(255,255,255,0.2)")),
                text=scatter_df["date"].dt.strftime("%Y-%m-%d"),
                hovertemplate="%{text}<br>Surge: %{x:.2f}<br>5d Ret: %{y:.2f}%<extra></extra>",
                showlegend=False,
            ))

            if len(scatter_df) >= 10:
                slope, intercept, r_val, *_ = scipy_stats.linregress(
                    scatter_df["surge_score"], scatter_df["ret_5d_pct"]
                )
                x_line = np.linspace(scatter_df["surge_score"].min(),
                                     scatter_df["surge_score"].max(), 50)
                fig_sc.add_trace(go.Scatter(
                    x=x_line, y=slope * x_line + intercept,
                    mode="lines", name=f"OLS  (r={r_val:.2f})",
                    line=dict(color=GOLD, width=1.5, dash="dash"),
                ))

            fig_sc.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dot"))
            fig_sc.update_layout(
                **BASE_LAYOUT,
                title=title_cfg(f"◈  Surge Score vs 5d Return  ·  {fwd_sym}"),
                height=400,
                xaxis=dict(**AXIS, title=dict(text="Surge Score", font=dict(color=MUTED))),
                yaxis=dict(**AXIS, title=dict(text="5d Forward Return %", font=dict(color=MUTED))),
                showlegend=True,
                legend=dict(bgcolor="rgba(0,0,0,0.6)", bordercolor="#1e2d45",
                            borderwidth=1, font=dict(size=11)),
            )
            st.plotly_chart(fig_sc, width='stretch')

        # ── Raw matched dates table ───────────────────────────
        with st.expander(
            f"📋  All {len(similar_hist)} Matched Historical Dates  ·  {fwd_sym}",
            expanded=False,
        ):
            show_fwd = similar_hist.copy()
            for c in ["Next_1d_Return","Next_2d_Return","Next_3d_Return",
                      "Next_5d_Return","Next_7d_Return"]:
                if c in show_fwd.columns:
                    show_fwd[c] = show_fwd[c] * 100
            show_fwd.columns = [
                c.replace("Next_","").replace("_Return"," Ret %").replace("_"," ")
                for c in show_fwd.columns
            ]
            show_fwd = show_fwd.sort_values("date", ascending=False).reset_index(drop=True)
            st.dataframe(
                show_fwd.style.format(
                    {c: "{:.2f}" for c in show_fwd.columns if "Ret" in c or "Score" in c},
                    na_rep="—"
                ),
                use_container_width=True, height=380,
            )


# ══════════════════════════════════════════════════════════════
#  FOOTER
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