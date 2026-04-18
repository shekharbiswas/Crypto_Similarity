"""
CRYPTO CHART DASHBOARD — C1/C2/C3  (DAILY + WEEKLY)
======================================================
Single Streamlit dashboard with a Daily / Weekly toggle.
Loads from:
  Daily  → ./data/crypto_with_indicators.csv
  Weekly → ./data/weekly_crypto_with_indicators.csv

All signal parameters, windows, and UI labels automatically
adapt to the selected timeframe.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
from datetime import timedelta

st.set_page_config(page_title="Crypto Chart", layout="wide", page_icon="₿")

# ════════════════════════════════════════════════════════════════════════════════
# TIMEFRAME CONFIG
# All bar-count parameters live here.  Everything downstream reads from cfg.
# ════════════════════════════════════════════════════════════════════════════════

TIMEFRAME_CFG = {
    "Daily": dict(
        csv_path        = "./data/crypto_with_indicators.csv",
        norm_window     = 252,   # bars for indicator normalisation (≈1 yr)
        pct_rank_win    = 10,    # rolling percentile-rank window
        pct_rank_win2   = 20,    # second percentile-rank window (C2)
        surge_roll      = 20,    # surge rolling mean/std window
        surge_roll_min  = 5,
        sr_primary      = 30,    # S/R primary lookback
        sr_fallback     = [60, 120, 200, 300],
        # C1/C2
        c1_window       = 5,
        c1_vol_bars     = 3,
        c1_mom_bars     = 2,
        ma_fast         = 20,    # MA used for confirmation & overlays
        ma_slow         = 50,
        ma_fast_label   = "MA 20",
        ma_slow_label   = "MA 50",
        ma_fast_key     = "MA_fast",
        ma_slow_key     = "MA_slow",
        await_consec    = 5,
        await_max_wait  = 15,
        await_exit_consec  = 5,
        await_exit_max  = 20,
        vol_avg_window  = 20,
        # Defaults for UI sliders
        def_min_move    = 2.0,
        def_fwd_window  = 7,
        def_c3_order    = 5,
        def_c3_min_sep  = 10,
        def_c3_max_bars = 120,
        def_c3_neck_wait= 30,
        def_c3_min_mag  = 15,
        def_surge_lb    = 3,
        fwd_label       = "Within days",
        bar_label       = "days",
        vol_label       = "Vol (daily)",
        x_title         = "Date",
        score_label     = "Score %ile (10d)",
        surge_label_ax  = "Surge",
        default_range_days = 365,
        min_bars        = 10,
        c1_desc         = "C1: Vol squeeze + Mom washout\nC2: Mom10d & Mom20d both <5",
        entry_htpl_top  = "<i>C1</i>: Vol squeeze + Mom washout<br><i>C2</i>: Mom10d & Mom20d both &lt;5 (≥2d in 5)<br>",
        exit_htpl_top   = "Momentum extreme high + vol contraction<br>",
        timeframe_badge = "",
        smooth_max      = 7,
        smooth_def      = 3,
    ),
    "Weekly": dict(
        csv_path        = "./data/weekly_crypto_with_indicators.csv",
        norm_window     = 52,
        pct_rank_win    = 4,
        pct_rank_win2   = 8,
        surge_roll      = 8,
        surge_roll_min  = 3,
        sr_primary      = 26,
        sr_fallback     = [52, 78, 104],
        # C1/C2
        c1_window       = 3,
        c1_vol_bars     = 2,
        c1_mom_bars     = 2,
        ma_fast         = 4,
        ma_slow         = 10,
        ma_fast_label   = "MA 4w (~20d)",
        ma_slow_label   = "MA 10w (~50d)",
        ma_fast_key     = "MA_fast",
        ma_slow_key     = "MA_slow",
        await_consec    = 2,
        await_max_wait  = 6,
        await_exit_consec  = 2,
        await_exit_max  = 8,
        vol_avg_window  = 4,
        # Defaults for UI sliders
        def_min_move    = 5.0,
        def_fwd_window  = 4,
        def_c3_order    = 3,
        def_c3_min_sep  = 4,
        def_c3_max_bars = 52,
        def_c3_neck_wait= 8,
        def_c3_min_mag  = 10,
        def_surge_lb    = 3,
        fwd_label       = "Within weeks",
        bar_label       = "weeks",
        vol_label       = "Vol (weekly sum)",
        x_title         = "Week ending (Friday)",
        score_label     = "Score %ile (4w)",
        surge_label_ax  = "Surge (wkly)",
        default_range_days = 730,
        min_bars        = 8,     # 8 weekly bars minimum to render chart
        c1_desc         = "C1: Vol squeeze + Mom washout (weekly)\nC2: Mom4w & Mom8w both <5",
        entry_htpl_top  = "<i>C1</i>: Vol squeeze + Mom washout (weekly)<br><i>C2</i>: Mom4w & Mom8w both &lt;5 (≥2w in 3)<br>",
        exit_htpl_top   = "Momentum extreme high + vol contraction (weekly)<br>",
        timeframe_badge = "WEEKLY",
        smooth_max      = 5,
        smooth_def      = 2,
    ),
}

# ── Shared constants ──────────────────────────────────────────────────────────
INDICATORS = {
    'Trend':      ['EMA_9','EMA_21','EMA_50','EMA_100','EMA_200',
                   'SMA_50','SMA_200','Supertrend_Direction','MACD','ADX','Aroon_Oscillator'],
    'Momentum':   ['RSI','Stoch_K','Stoch_D','Williams_R','CCI','ROC_14','TSI'],
    'Volume':     ['OBV','MFI','AD_Line','CMF','Volume_ROC'],
    'Volatility': ['ATR','BB_Width','BB_Percent'],
    'Structure':  ['Higher_Highs','Higher_Lows','Pivot','R1','S1'],
}
INDICATOR_WEIGHTS = {
    'Trend': {'EMA_9':0.5,'EMA_21':0.5,'EMA_50':1,'EMA_100':1.5,'EMA_200':2,
              'SMA_50':1,'SMA_200':2,'Supertrend_Direction':2,'MACD':2,'ADX':2,'Aroon_Oscillator':1}
}
OVERLAY_COLORS = {
    'Trend':'#FF6B6B','Momentum':'#C62828','Volume':'#26A69A',
    'Volatility':'#6A1B9A','Structure':'#1565C0',
}
SCORE_STYLE = {
    'Structure':  dict(color='#1565C0', width=1.8),
    'Momentum':   dict(color='#C62828', width=1.8),
    'Volatility': dict(color='#6A1B9A', width=2.0),
}
MA_STYLE = {
    'fast': dict(color='#757575', width=1.3, dash='dash'),
    'slow': dict(color='#5C6BC0', width=1.3, dash='dash'),
}
SL_ATR_MULT = 1.5
SL_CAP_PCT  = 0.03


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def normalize_indicator(series, window=252):
    expanding_med = series.expanding(min_periods=1).median()
    s  = series.fillna(expanding_med)
    mn = s.rolling(window, min_periods=max(5, window // 10)).min()
    mx = s.rolling(window, min_periods=max(5, window // 10)).max()
    return ((s - mn) / (mx - mn + 1e-9)).clip(0, 1).mul(100).fillna(50)

def rolling_pct_rank(series, window=10):
    arr = series.values.astype(float)
    res = np.full(len(arr), np.nan)
    for i in range(window - 1, len(arr)):
        w     = arr[i - window + 1: i + 1]
        valid = w[~np.isnan(w)]
        n     = len(valid)
        if n < max(2, window // 2): continue
        res[i] = 50.0 if n == 1 else (valid < arr[i]).sum() / (n - 1) * 100
    return pd.Series(res, index=series.index)

def smooth(series, window=3):
    if window <= 1: return series
    return series.rolling(window, min_periods=1, center=False, win_type='gaussian').mean(std=1.0)

def scale_to_price(score, price_series, lower_frac=0.05, upper_frac=0.35):
    pmin   = price_series.min()
    prange = price_series.max() - pmin
    if prange == 0: prange = 1.0
    return (pmin + prange * lower_frac) + (score / 100.0) * (prange * (upper_frac - lower_frac))

def calculate_category_scores(df, cfg):
    out = {}
    for cat, inds in INDICATORS.items():
        wv, wt = [], []
        for ind in inds:
            if ind not in df.columns: continue
            try:
                w = INDICATOR_WEIGHTS.get(cat, {}).get(ind, 1)
                wv.append(normalize_indicator(df[ind], cfg['norm_window']) * w)
                wt.append(w)
            except: pass
        out[cat] = sum(wv) / sum(wt) if wv else pd.Series(50, index=df.index)
    return pd.DataFrame(out)

def calculate_mas(df, cfg):
    return pd.DataFrame({
        'MA_fast': df['close'].rolling(cfg['ma_fast'], min_periods=cfg['ma_fast']).mean(),
        'MA_slow': df['close'].rolling(cfg['ma_slow'], min_periods=cfg['ma_slow']).mean(),
    }, index=df.index)


def compute_trend_score(df, cfg):
    """
    Bar-by-bar trend score with TWO components returned as a named dict.
    Only uses data available at each bar (no lookahead).

    ma_score  (0–2)  — structural price-vs-MA conditions ONLY.
                        This is what the user cares about most:
                        "price still above MA20 and MA50".
      +1  close > MA_fast  (MA20 daily / MA4w weekly)
      +1  close > MA_slow  (MA50 daily / MA10w weekly)

    full_score (0–5) — all conditions including momentum context:
      +1  close > MA_fast
      +1  close > MA_slow
      +1  MA_fast > MA_slow  (golden-cross zone)
      +1  Supertrend direction = bullish
      +1  EMA_50 slope positive over last slope_lb bars

    The gate in apply_entry_quality_gate checks ma_score by default so a
    momentum washout (C1/C2 condition) while price is above both MAs always
    passes — even if Supertrend has flipped or EMA50 slope is flat.
    The user can optionally require a higher full_score for stricter filtering.

    Returns two pd.Series (ma_score, full_score) both aligned to df.index.
    """
    cl       = df['close'].values.astype(float)
    n        = len(df)
    ma_f     = df['close'].rolling(cfg['ma_fast'], min_periods=cfg['ma_fast']).mean().values
    ma_s     = df['close'].rolling(cfg['ma_slow'], min_periods=cfg['ma_slow']).mean().values
    st_dir   = df['Supertrend_Direction'].values.astype(float) \
               if 'Supertrend_Direction' in df.columns else np.full(n, np.nan)
    ema50    = df['EMA_50'].values.astype(float) \
               if 'EMA_50' in df.columns \
               else df['close'].ewm(span=50, adjust=False).mean().values

    slope_lb  = max(3, cfg['ma_fast'] // 5)
    ma_score  = np.zeros(n, dtype=int)
    full_score = np.zeros(n, dtype=int)

    for i in range(n):
        above_fast = not np.isnan(ma_f[i]) and cl[i] > ma_f[i]
        above_slow = not np.isnan(ma_s[i]) and cl[i] > ma_s[i]
        fast_gt_slow = (not np.isnan(ma_f[i]) and not np.isnan(ma_s[i])
                        and ma_f[i] > ma_s[i])
        st_bull = not np.isnan(st_dir[i]) and st_dir[i] == 1
        ema_rising = (i >= slope_lb
                      and not np.isnan(ema50[i])
                      and not np.isnan(ema50[i - slope_lb])
                      and ema50[i] > ema50[i - slope_lb])

        ms = int(above_fast) + int(above_slow)
        fs = ms + int(fast_gt_slow) + int(st_bull) + int(ema_rising)

        ma_score[i]   = ms
        full_score[i] = fs

    return pd.Series(ma_score, index=df.index), pd.Series(full_score, index=df.index)


# ════════════════════════════════════════════════════════════════════════════════
# SIGNAL DETECTION
# ════════════════════════════════════════════════════════════════════════════════

def apply_entry_quality_gate(sig, full_df, cfg,
                              require_vol_spike, vol_spike_mult,
                              require_rsi, rsi_max,
                              require_adx, adx_max,
                              require_above_ma_slow,
                              require_positive_trend=False,
                              trend_ma_scores=None,
                              trend_full_scores=None,
                              trend_min_ma_score=2,
                              trend_min_full_score=3):
    """
    Filter C1/C2 entry signals bar-by-bar using only data known AT each bar.

    Standard filters (unchanged):
      vol_spike, rsi_oversold, adx_weak, above_ma_slow

    Positive Trend gate (require_positive_trend):
    ───────────────────────────────────────────────
    Uses TWO separate score thresholds so the gate is never accidentally
    triggered by indicators that are SUPPOSED to be low at C1/C2 entry time.

    trend_min_ma_score (0–2, default 2):
        Both MA conditions must hold:
          close > MA_fast  AND  close > MA_slow
        This is the PRIMARY check — exactly what the user described:
        "price above MA20 and MA50".  A momentum washout (C1/C2 trigger)
        while price holds above both MAs is a healthy pullback and should
        ALWAYS produce a green diamond.

    trend_min_full_score (0–5, default 3):
        Stricter optional check that also requires MA alignment +
        Supertrend/EMA slope conditions.  Only applied if ma_score
        already passed — i.e. both MAs are respected AND broader
        trend structure is present.

    Gate logic:
        PASS  if  ma_score[i] >= trend_min_ma_score
                  AND full_score[i] >= trend_min_full_score
        BLOCK otherwise (reason = 'trend_ma' or 'trend_full')

    Setting trend_min_ma_score=2 and trend_min_full_score=0 gives
    "only show when above both MAs" with no other trend restriction.
    """
    cl      = full_df['close'].values.astype(float)
    vol     = full_df['volume_usd'].values.astype(float) if 'volume_usd' in full_df.columns else np.ones(len(full_df))
    rsi     = full_df['RSI'].values.astype(float)        if 'RSI' in full_df.columns else np.full(len(full_df), 50.0)
    adx     = full_df['ADX'].values.astype(float)        if 'ADX' in full_df.columns else np.zeros(len(full_df))
    vol_avg = pd.Series(vol).rolling(cfg['vol_avg_window'], min_periods=2).mean().values
    ma_slow = full_df['close'].rolling(cfg['ma_slow'], min_periods=cfg['ma_slow']).mean().values

    n   = len(full_df)
    tms = trend_ma_scores.values   if trend_ma_scores   is not None else np.zeros(n)
    tfs = trend_full_scores.values if trend_full_scores is not None else np.zeros(n)

    out = sig.copy()
    for i in np.where(sig.values)[0]:
        reasons = []
        if require_vol_spike:
            avg = vol_avg[i]
            if np.isnan(avg) or avg <= 0 or vol[i] < vol_spike_mult * avg:
                reasons.append('vol')
        if require_rsi:
            if not np.isnan(rsi[i]) and rsi[i] >= rsi_max:
                reasons.append('rsi')
        if require_adx:
            if not np.isnan(adx[i]) and adx[i] >= adx_max:
                reasons.append('adx')
        if require_above_ma_slow:
            if not np.isnan(ma_slow[i]) and cl[i] < ma_slow[i]:
                reasons.append('ma_slow')
        if require_positive_trend:
            # MA check: must be above both MAs (primary condition)
            if int(tms[i]) < trend_min_ma_score:
                reasons.append('trend_ma')
            # Full score check: only if MA check passed
            elif trend_min_full_score > 0 and int(tfs[i]) < trend_min_full_score:
                reasons.append('trend_full')
        if reasons:
            out.iloc[i] = False
    return out


def detect_surge(mom, cfg, lookback=3, threshold=10):
    ac    = mom.diff(lookback)
    pc    = mom.pct_change(lookback) * 100
    accel = mom.diff().diff()
    rm    = mom.rolling(cfg['surge_roll'], min_periods=cfg['surge_roll_min']).mean()
    rs    = mom.rolling(cfg['surge_roll'], min_periods=cfg['surge_roll_min']).std()
    z     = (mom - rm) / (rs + 1e-10)
    sc    = pd.Series(0.0, index=mom.index)
    for i in range(lookback, len(mom)):
        sc.iloc[i] = (
            ac.iloc[i] * 0.4
            + (pc.iloc[i]    if not pd.isna(pc.iloc[i])    else 0) * 0.3
            + (accel.iloc[i] if not pd.isna(accel.iloc[i]) else 0) * 2.0
            + (z.iloc[i]     if not pd.isna(z.iloc[i])     else 0) * 3.0
        )
    sig = pd.Series(0, index=mom.index)
    sig[sc >  threshold] =  1
    sig[sc < -threshold] = -1
    return sc, sig

def surge_label(sig, sc):
    if sig ==  1: return ("🚀 EXPLOSIVE" if sc > 30 else "⚡ STRONG" if sc > 20 else "📈 SURGE"),  "#00C853"
    if sig == -1: return ("💥 SHARP DROP" if sc < -30 else "⚠️ STRONG DROP" if sc < -20 else "📉 DROP"), "#D32F2F"
    return "➡️ NEUTRAL", "#BDBDBD"


def detect_c1(pct_vol, pct_mom, cfg, vol_thresh=95, mom_thresh=5, cooldown_vol=70):
    vol_arr = pct_vol.values.astype(float)
    mom_arr = pct_mom.values.astype(float)
    sig     = np.zeros(len(pct_vol), dtype=bool)
    in_cd   = False
    window  = cfg['c1_window']
    for i in range(window - 1, len(pct_vol)):
        if in_cd:
            if not np.isnan(vol_arr[i]) and vol_arr[i] < cooldown_vol: in_cd = False
            else: continue
        v_win = vol_arr[i - window + 1: i + 1]
        m_win = mom_arr[i - window + 1: i + 1]
        if (int(np.nansum(v_win >= vol_thresh)) >= cfg['c1_vol_bars'] and
                int(np.nansum(m_win <= mom_thresh)) >= cfg['c1_mom_bars']):
            sig[i] = True; in_cd = True
    return pd.Series(sig, index=pct_vol.index)

def detect_c2(pct_mom_fast, pct_mom_slow, cfg, thresh=2):
    m_f = pct_mom_fast.values.astype(float)
    m_s = pct_mom_slow.values.astype(float)
    sig = np.zeros(len(m_f), dtype=bool)
    window   = cfg['c1_window']
    mom_bars = cfg['c1_mom_bars']
    for i in range(window - 1, len(m_f)):
        wf = m_f[i - window + 1: i + 1]
        ws = m_s[i - window + 1: i + 1]
        if int(np.nansum((wf < thresh) & (ws < thresh))) >= mom_bars:
            sig[i] = True
    return pd.Series(sig, index=pct_mom_fast.index)

def await_ma_above(sig, close, ma, cfg):
    cl  = close.values.astype(float)
    ma_ = ma.values.astype(float)
    raw = sig.values.astype(bool)
    out = np.zeros(len(raw), dtype=bool)
    n   = len(raw)
    for i in np.where(raw)[0]:
        streak = 0
        for j in range(i, min(i + cfg['await_max_wait'] + 1, n)):
            if np.isnan(ma_[j]): streak = 0; continue
            if cl[j] > ma_[j]:
                streak += 1
                if streak >= cfg['await_consec']: out[j] = True; break
            else: streak = 0
    return pd.Series(out, index=sig.index)

def await_ma_below(sig, close, ma, cfg):
    cl  = close.values.astype(float)
    ma_ = ma.values.astype(float)
    raw = sig.values.astype(bool)
    out = np.zeros(len(raw), dtype=bool)
    n   = len(raw)
    for i in np.where(raw)[0]:
        streak = 0
        for j in range(i, min(i + cfg['await_exit_max'] + 1, n)):
            if np.isnan(ma_[j]): streak = 0; continue
            if cl[j] < ma_[j]:
                streak += 1
                if streak >= cfg['await_exit_consec']: out[j] = True; break
            else: streak = 0
    return pd.Series(out, index=sig.index)


# ── C3: Double Bottom / Double Top ────────────────────────────────────────────

def _find_swings(arr, order=5, kind='low'):
    n      = len(arr)
    result = []
    for i in range(order, n - order):
        left  = arr[i - order: i]
        right = arr[i + 1: i + order + 1]
        if kind == 'low'  and arr[i] <= np.nanmin(left) and arr[i] <= np.nanmin(right):
            result.append((i, arr[i]))
        if kind == 'high' and arr[i] >= np.nanmax(left) and arr[i] >= np.nanmax(right):
            result.append((i, arr[i]))
    return result

def detect_c3_double_bottom(close, low, high,
                             order=5, min_sep=10, max_bars=120,
                             price_tol=0.04, max_neckline_wait=30,
                             min_magnitude=0.05):
    cl  = np.array(close, dtype=float)
    lo  = np.array(low,   dtype=float)
    n   = len(cl)
    sig = np.zeros(n, dtype=bool)
    patterns = []
    swing_lows = _find_swings(lo, order=order, kind='low')
    used = set()
    for idx2, (b2, p2) in enumerate(swing_lows):
        for b1, p1 in reversed(swing_lows[:idx2]):
            gap = b2 - b1
            if gap < min_sep:  continue
            if gap > max_bars: break
            if abs(p1 - p2) / (max(p1, p2) + 1e-9) > price_tol: continue
            neck = np.nanmax(cl[b1: b2 + 1])
            if neck <= max(p1, p2) * 1.01: continue
            avg_bottom = (p1 + p2) / 2.0
            if (neck - avg_bottom) / (avg_bottom + 1e-9) < min_magnitude: continue
            for j in range(b2 + order + 1, min(b2 + order + max_neckline_wait + 1, n)):
                if cl[j] > neck and j not in used:
                    sig[j] = True; used.add(j)
                    patterns.append(dict(type='double_bottom', l1_bar=b1, l2_bar=b2,
                                         l1_price=p1, l2_price=p2, neckline=neck, breakout_bar=j))
                    break
            break
    return pd.Series(sig, index=pd.RangeIndex(n)), patterns

def detect_c3_double_top(close, low, high,
                          order=5, min_sep=10, max_bars=120,
                          price_tol=0.04, max_neckline_wait=30,
                          min_magnitude=0.05):
    cl  = np.array(close, dtype=float)
    hi  = np.array(high,  dtype=float)
    n   = len(cl)
    sig = np.zeros(n, dtype=bool)
    patterns = []
    swing_highs = _find_swings(hi, order=order, kind='high')
    used = set()
    for idx2, (b2, p2) in enumerate(swing_highs):
        for b1, p1 in reversed(swing_highs[:idx2]):
            gap = b2 - b1
            if gap < min_sep:  continue
            if gap > max_bars: break
            if abs(p1 - p2) / (max(p1, p2) + 1e-9) > price_tol: continue
            neck = np.nanmin(cl[b1: b2 + 1])
            if neck >= min(p1, p2) * 0.99: continue
            avg_top = (p1 + p2) / 2.0
            if (avg_top - neck) / (avg_top + 1e-9) < min_magnitude: continue
            for j in range(b2 + order + 1, min(b2 + order + max_neckline_wait + 1, n)):
                if cl[j] < neck and j not in used:
                    sig[j] = True; used.add(j)
                    patterns.append(dict(type='double_top', l1_bar=b1, l2_bar=b2,
                                         l1_price=p1, l2_price=p2, neckline=neck, breakout_bar=j))
                    break
            break
    return pd.Series(sig, index=pd.RangeIndex(n)), patterns

def add_c3_pattern_shapes(fig, dates, close_arr, low_arr, high_arr, patterns, row=1):
    for p in patterns:
        is_bottom = (p['type'] == 'double_bottom')
        color     = '#00BFA5' if is_bottom else '#FF6D00'
        b1 = p['l1_bar']; b2 = p['l2_bar']; bk = p['breakout_bar']
        neck = p['neckline']
        fig.add_shape(type='line', x0=dates[b1], x1=dates[bk], y0=neck, y1=neck,
            line=dict(color=color, width=1.2, dash='dash'), row=row, col=1)
        lvl = (p['l1_price'] + p['l2_price']) / 2
        fig.add_shape(type='line', x0=dates[b1], x1=dates[b2], y0=lvl, y1=lvl,
            line=dict(color=color, width=0.8, dash='dot'), row=row, col=1)
        y_l1 = low_arr[b1]  * 0.993 if is_bottom else high_arr[b1] * 1.007
        y_l2 = low_arr[b2]  * 0.993 if is_bottom else high_arr[b2] * 1.007
        fig.add_trace(go.Scatter(x=[dates[b1], dates[b2]], y=[y_l1, y_l2], mode='markers',
            showlegend=False, hoverinfo='skip',
            marker=dict(symbol='circle-open', size=9, color='rgba(0,0,0,0)',
                        line=dict(width=1.5, color=color)),
        ), row=row, col=1, secondary_y=False)


# ── S/R levels ────────────────────────────────────────────────────────────────

def _swing_sr(i, high, low, close, volume, lookback=30, order=6, n=2, touch_band=0.005):
    start   = max(order, i - lookback)
    price_i = close[i]
    vol_avg = np.nanmean(volume[max(0, i - lookback): i]) if i > 0 else 1.0
    if vol_avg <= 0: vol_avg = 1.0
    raw_res, raw_sup = [], []
    for j in range(start, i - order):
        if j - order < 0: continue
        hi_win = high[j - order: j + order + 1]
        if (len(hi_win) == 2*order+1 and high[j] == np.max(hi_win)
                and high[j] > high[j-1] and high[j] > high[j+1] and high[j] > price_i):
            raw_res.append((high[j], volume[j]))
        lo_win = low[j - order: j + order + 1]
        if (len(lo_win) == 2*order+1 and low[j] == np.min(lo_win)
                and low[j] < low[j-1] and low[j] < low[j+1] and low[j] < price_i):
            raw_sup.append((low[j], volume[j]))

    def score_dedup(cands, reverse):
        if not cands: return []
        groups = []
        for level, vol in sorted(cands, key=lambda x: x[0], reverse=reverse):
            placed = False
            for g in groups:
                if abs(level - g['levels'][0]) / max(g['levels'][0], 1e-9) <= touch_band:
                    g['levels'].append(level); g['vols'].append(vol); placed = True; break
            if not placed: groups.append({'levels': [level], 'vols': [vol]})
        scored = []
        for g in groups:
            tc    = len(g['levels'])
            score = tc * (np.mean(g['vols']) / vol_avg)
            scored.append((np.mean(g['levels']), score, tc))
        return sorted(scored, key=lambda x: -x[1])[:n]

    return score_dedup(raw_sup, True), score_dedup(raw_res, False)

def _swing_sr_fallback(i, high, low, close, volume, cfg):
    sup, res = _swing_sr(i, high, low, close, volume, lookback=cfg['sr_primary'])
    price    = close[i]
    if not sup or not res:
        for lb in cfg['sr_fallback']:
            sw, rw = _swing_sr(i, high, low, close, volume, lookback=lb)
            if not sup and sw: sup = sorted(sw, key=lambda x: abs(x[0]-price))[:2]
            if not res and rw: res = sorted(rw, key=lambda x: abs(x[0]-price))[:2]
            if sup and res: break
    return sup, res

def build_sr_customdata(sig, full_df, cfg, signal_type='green'):
    high   = full_df['high'].values.astype(float)
    low    = full_df['low'].values.astype(float)
    close  = full_df['close'].values.astype(float)
    volume = full_df['volume_usd'].values.astype(float) if 'volume_usd' in full_df.columns \
             else np.ones(len(full_df))
    atr_arr = full_df['ATR'].values.astype(float) if 'ATR' in full_df.columns \
              else pd.Series(high - low).rolling(14, min_periods=3).mean().values
    labels = []
    for i in np.where(sig.values)[0]:
        price        = close[i]
        sup_s, res_s = _swing_sr_fallback(i, high, low, close, volume, cfg)
        def fmt(scored):
            if not scored: return 'none found'
            return '  '.join(f"${lv:.4g}({'★'*min(tc,3)})" for lv, sc, tc in scored)
        atr = atr_arr[i] if not np.isnan(atr_arr[i]) else (high[i] - low[i])
        if signal_type == 'green':
            sl     = max(price - SL_ATR_MULT * atr, price * (1.0 - SL_CAP_PCT))
            sl_str = f"Stop: ${sl:.4g}  ({(price-sl)/price*100:.1f}% below)"
        else:
            sl     = min(price + SL_ATR_MULT * atr, price * (1.0 + SL_CAP_PCT))
            sl_str = f"Stop: ${sl:.4g}  ({(sl-price)/price*100:.1f}% above)"
        labels.append((fmt(sup_s), fmt(res_s), sl_str))
    return labels

def classify_signal_quality(sig, close_arr, direction, fwd_window, min_pct):
    n         = len(close_arr)
    confirmed = np.zeros(n, dtype=bool)
    failed    = np.zeros(n, dtype=bool)
    for i in np.where(sig.values)[0]:
        ep = close_arr[i]
        if ep <= 0 or np.isnan(ep): failed[i] = True; continue
        wp = close_arr[i + 1: min(i + fwd_window + 1, n)]
        if len(wp) == 0: failed[i] = True; continue
        best = (np.nanmax(wp) - ep) / ep * 100 if direction == 'up' \
               else (ep - np.nanmin(wp)) / ep * 100
        if best >= min_pct: confirmed[i] = True
        else:               failed[i]    = True
    return pd.Series(confirmed, index=sig.index), pd.Series(failed, index=sig.index)

def detect_atr_stop_hit(sig_green, close_arr, low_arr, atr_arr, ma_fast_arr,
                        profit_threshold_pct=20.0,
                        atr_mult=1.5,
                        max_lookahead=None):
    """
    State-machine exit detector.  Processes entries in chronological order
    with ONE active trade at a time.

    State transitions
    -----------------
    FLAT -> WATCHING
        When a green entry bar fires AND no trade is currently active.
        Entries that arrive while a trade is still open are SKIPPED entirely.

    WATCHING -> profit gate cleared
        Scan forward bar-by-bar.  Track the running peak gain.
        Once peak >= profit_threshold_pct the trade is "armed".

    ARMED -> EXIT  (whichever fires FIRST on each bar)
        Condition A - MA cross exit (early warning, often fires first):
            close[j] < ma_fast_arr[j]
        Condition B - ATR hard stop:
            low[j] <= entry_close - atr_mult x ATR[entry]

    EXIT -> FLAT
        Trade is closed.  Next green entry after this bar opens a fresh watch.

    Returns
    -------
    stop_hit : pd.Series bool  -- True on exit bar
    meta     : list of dicts   with keys
                 entry_bar, stop_bar, entry_price, stop_level,
                 peak_pct, exit_type  ('atr_stop' | 'ma_cross' | 'both'),
                 atr_mult
    """
    n        = len(close_arr)
    stop_hit = np.zeros(n, dtype=bool)
    meta     = []

    entry_bars   = list(np.where(sig_green.values)[0])
    next_allowed = 0   # earliest bar a new entry may open

    for i in entry_bars:
        if i < next_allowed:
            continue   # skip — previous trade still open

        ep = close_arr[i]
        if ep <= 0 or np.isnan(ep):
            continue

        atr_val    = atr_arr[i] if not np.isnan(atr_arr[i]) else ep * 0.02
        stop_level = ep - atr_mult * atr_val
        end        = n if max_lookahead is None else min(i + max_lookahead + 1, n)

        # Phase 1 — scan the FULL window to find:
        #   (a) whether the profit gate was ever reached  → arms the trade
        #   (b) the bar of MAXIMUM gain                   → peak_bar
        #
        # Why scan all the way to the end rather than breaking on gate-cross?
        # If we break as soon as +20% is hit, Phase 2 starts at that early bar
        # and may fire an exit before the price has finished its run.  The gate
        # only controls WHETHER a trade gets armed — not WHERE exit watching
        # begins.  Exit watching must start from the true peak bar so the SL
        # fires on the way DOWN, not on the way up through the gate.
        #
        # No future data is used: we are simulating a forward scan bar-by-bar
        # exactly as a trader watching in real time would — we just do it in one
        # pass instead of a live loop.
        peak_pct  = 0.0
        peak_bar  = i          # bar of highest close so far (initialise to entry)
        armed     = False
        gate_bar  = None       # first bar that crossed the profit gate

        for j in range(i + 1, end):
            pct = (close_arr[j] - ep) / ep * 100
            if pct > peak_pct:
                peak_pct = pct
                peak_bar = j
            if not armed and peak_pct >= profit_threshold_pct:
                armed    = True
                gate_bar = j   # record but do NOT break — keep scanning for peak

        if not armed:
            next_allowed = end
            continue

        # Phase 2 — start from the bar AFTER the true peak.
        # The peak close is already known; the next bar is the earliest we could
        # observe a reversal and act.  This ensures the exit fires on the way
        # down from the peak, not while price is still climbing.
        exit_bar  = None
        exit_type = None

        for j in range(peak_bar + 1, end):
            pct = (close_arr[j] - ep) / ep * 100
            if pct > peak_pct:
                peak_pct = pct

            ma_val   = ma_fast_arr[j] if (ma_fast_arr is not None and not np.isnan(ma_fast_arr[j])) else np.nan
            ma_cross = (not np.isnan(ma_val)) and (close_arr[j] < ma_val)
            atr_hit  = low_arr[j] <= stop_level

            if ma_cross or atr_hit:
                exit_bar  = j
                exit_type = ('both'     if (ma_cross and atr_hit)  else
                             'ma_cross' if ma_cross                 else
                             'atr_stop')
                break

        if exit_bar is not None:
            stop_hit[exit_bar] = True
            meta.append(dict(
                entry_bar   = i,
                stop_bar    = exit_bar,
                entry_price = ep,
                stop_level  = stop_level,
                peak_pct    = peak_pct,
                exit_type   = exit_type,
                atr_mult    = atr_mult,
            ))
            next_allowed = exit_bar + 1
        else:
            next_allowed = end

    return pd.Series(stop_hit, index=sig_green.index), meta

def add_pulse_halos(fig, dates, y_pos, color, row=1):
    for size, opacity in [(22, 0.6), (15, 0.8)]:
        fig.add_trace(go.Scatter(
            x=dates, y=y_pos, mode='markers', showlegend=False, hoverinfo='skip',
            marker=dict(symbol='diamond-open', size=size, color='rgba(0,0,0,0)',
                        line=dict(width=2, color=color), opacity=opacity),
        ), row=row, col=1, secondary_y=False)


# ════════════════════════════════════════════════════════════════════════════════
# DATA LOADER  (cached per CSV path)
# ════════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data(csv_path: str):
    df = pd.read_csv(csv_path, parse_dates=['date'])
    df = df.rename(columns={'date': 'Date'})
    df = df.sort_values(['symbol', 'Date']).reset_index(drop=True)
    return df, sorted(df['symbol'].unique())


# ════════════════════════════════════════════════════════════════════════════════
# CHART BUILDER
# ════════════════════════════════════════════════════════════════════════════════

def create_chart(full, cfg, symbol, sel_overlays,
                 show_surge, surge_lb, surge_thr,
                 d0, d1,
                 show_ma_fast, show_ma_slow,
                 show_str, show_mom, show_vol_score, smooth_window,
                 show_sb, fwd_window, min_move_pct,
                 show_c3, c3_order, c3_min_sep, c3_max_bars,
                 c3_price_tol, c3_neck_wait, c3_min_magnitude,
                 c12_vol_spike, c12_vol_mult,
                 c12_rsi_filter, c12_rsi_max,
                 c12_adx_filter, c12_adx_max,
                 c12_ma_slow_filter,
                 c12_trend_filter=True,
                 c12_trend_min_ma_score=2,
                 c12_trend_min_full_score=0,
                 show_atr_stop=True,
                 atr_stop_profit_pct=20.0,
                 atr_stop_mult=1.5):

    bl = cfg['bar_label']   # "days" or "weeks"

    cat  = calculate_category_scores(full, cfg)
    mas  = calculate_mas(full, cfg)
    # ma_score  (0–2): purely close vs MA_fast / MA_slow — the primary gate
    # full_score (0–5): includes golden cross, Supertrend, EMA slope
    trend_ma_scores, trend_full_scores = compute_trend_score(full, cfg)

    pct_fast = pd.DataFrame(index=full.index)
    for c in ['Structure', 'Momentum', 'Volatility']:
        pct_fast[c] = rolling_pct_rank(cat[c], cfg['pct_rank_win']) if c in cat.columns \
                      else pd.Series(np.nan, index=full.index)

    surge_sc_f = surge_sig_f = None
    if show_surge and 'Momentum' in cat.columns:
        surge_sc_f, surge_sig_f = detect_surge(cat['Momentum'], cfg, surge_lb, surge_thr)

    # ── C1 + C2 ───────────────────────────────────────────────────────────────
    sb_green_f = sb_red_f = None
    if show_sb and 'Volatility' in pct_fast.columns and 'Momentum' in pct_fast.columns:
        pct_slow_mom = rolling_pct_rank(cat['Momentum'], cfg['pct_rank_win2']) \
                       if 'Momentum' in cat.columns else pd.Series(np.nan, index=full.index)
        c1_sig    = detect_c1(pct_fast['Volatility'], pct_fast['Momentum'], cfg)
        c2_sig    = detect_c2(pct_fast['Momentum'], pct_slow_mom, cfg)
        raw_entry = c1_sig | c2_sig
        ma_fast_s = full['close'].rolling(cfg['ma_fast'], min_periods=cfg['ma_fast']).mean()

        sb_green_f = raw_entry.copy()
        if sb_green_f.any():
            sb_green_f = apply_entry_quality_gate(
                sb_green_f, full, cfg,
                require_vol_spike=c12_vol_spike,   vol_spike_mult=c12_vol_mult,
                require_rsi=c12_rsi_filter,        rsi_max=c12_rsi_max,
                require_adx=c12_adx_filter,        adx_max=c12_adx_max,
                require_above_ma_slow=c12_ma_slow_filter,
                require_positive_trend=c12_trend_filter,
                trend_ma_scores=trend_ma_scores,
                trend_full_scores=trend_full_scores,
                trend_min_ma_score=c12_trend_min_ma_score,
                trend_min_full_score=c12_trend_min_full_score,
            )
        exit_raw  = detect_c1(
            pct_fast['Volatility'].apply(lambda x: 100 - x),
            pct_fast['Momentum'].apply(lambda x: 100 - x),
            cfg,
        )
        sb_red_f = await_ma_below(exit_raw, full['close'], ma_fast_s, cfg)

    # ── C3 ────────────────────────────────────────────────────────────────────
    c3_bull_f = c3_bear_f = None
    c3_bull_patterns_f = c3_bear_patterns_f = []

    if show_c3:
        fc = full['close'].values.astype(float)
        fl = full['low'].values.astype(float)
        fh = full['high'].values.astype(float)
        c3_bull_raw, c3_bull_patterns_f = detect_c3_double_bottom(
            fc, fl, fh, order=c3_order, min_sep=c3_min_sep, max_bars=c3_max_bars,
            price_tol=c3_price_tol, max_neckline_wait=c3_neck_wait,
            min_magnitude=c3_min_magnitude)
        c3_bear_raw, c3_bear_patterns_f = detect_c3_double_top(
            fc, fl, fh, order=c3_order, min_sep=c3_min_sep, max_bars=c3_max_bars,
            price_tol=c3_price_tol, max_neckline_wait=c3_neck_wait,
            min_magnitude=c3_min_magnitude)
        c3_bull_f = pd.Series(c3_bull_raw.values, index=full.index)
        c3_bear_f = pd.Series(c3_bear_raw.values, index=full.index)

    # ── Forward-return quality ─────────────────────────────────────────────────
    close_arr    = full['close'].values.astype(float)
    green_conf_f = green_fail_f = red_conf_f = red_fail_f = None
    if sb_green_f is not None:
        green_conf_f, green_fail_f = classify_signal_quality(sb_green_f, close_arr, 'up',   fwd_window, min_move_pct)
    if sb_red_f is not None:
        red_conf_f,   red_fail_f   = classify_signal_quality(sb_red_f,   close_arr, 'down', fwd_window, min_move_pct)

    c3_bull_conf_f = c3_bull_fail_f = c3_bear_conf_f = c3_bear_fail_f = None
    if c3_bull_f is not None:
        c3_bull_conf_f, c3_bull_fail_f = classify_signal_quality(c3_bull_f, close_arr, 'up',   fwd_window, min_move_pct)
    if c3_bear_f is not None:
        c3_bear_conf_f, c3_bear_fail_f = classify_signal_quality(c3_bear_f, close_arr, 'down', fwd_window, min_move_pct)

    # ── ATR + MA-cross exit signals (C1/C2 and C3) ───────────────────────────
    # Computed on the FULL series (pre-mask) — entries may precede the view
    # window, so we need the full history to get accurate exit bars.
    # The fast MA array is passed so the state machine can check MA-cross exit
    # (close < MA_fast) BEFORE the hard ATR stop on every bar.
    atr_stop_f    = None
    atr_stop_meta = []
    c3_atr_stop_f    = None
    c3_atr_stop_meta = []

    if show_atr_stop:
        low_arr_full  = full['low'].values.astype(float)
        atr_arr_full  = (full['ATR'].values.astype(float)
                         if 'ATR' in full.columns
                         else pd.Series(full['high'].values - full['low'].values)
                                .rolling(14, min_periods=3).mean().values)
        # Fast MA for the MA-cross exit condition
        ma_fast_full  = (full['close']
                         .rolling(cfg['ma_fast'], min_periods=cfg['ma_fast'])
                         .mean().values.astype(float))

        if sb_green_f is not None and sb_green_f.any():
            atr_stop_f, atr_stop_meta = detect_atr_stop_hit(
                sb_green_f, close_arr, low_arr_full, atr_arr_full, ma_fast_full,
                profit_threshold_pct = atr_stop_profit_pct,
                atr_mult             = atr_stop_mult,
            )

        if c3_bull_f is not None and c3_bull_f.any():
            c3_atr_stop_f, c3_atr_stop_meta = detect_atr_stop_hit(
                c3_bull_f, close_arr, low_arr_full, atr_arr_full, ma_fast_full,
                profit_threshold_pct = atr_stop_profit_pct,
                atr_mult             = atr_stop_mult,
            )

    # ── Date mask ─────────────────────────────────────────────────────────────
    mask = (full['Date'].dt.date >= d0) & (full['Date'].dt.date <= d1)
    sd   = full[mask].reset_index(drop=True)
    cs   = cat[mask].reset_index(drop=True)
    ma   = mas[mask].reset_index(drop=True)
    p_f  = pct_fast[mask].reset_index(drop=True)

    def _mask(s): return s[mask].reset_index(drop=True) if s is not None else None

    s_sc      = _mask(surge_sc_f);   s_sg      = _mask(surge_sig_f)
    sb_green  = _mask(sb_green_f);   sb_red    = _mask(sb_red_f)
    green_conf= _mask(green_conf_f); green_fail= _mask(green_fail_f)
    red_conf  = _mask(red_conf_f);   red_fail  = _mask(red_fail_f)
    c3_bull   = _mask(c3_bull_f);    c3_bear   = _mask(c3_bear_f)
    c3_bull_conf = _mask(c3_bull_conf_f); c3_bull_fail = _mask(c3_bull_fail_f)
    c3_bear_conf = _mask(c3_bear_conf_f); c3_bear_fail = _mask(c3_bear_fail_f)
    atr_stop     = _mask(atr_stop_f)
    c3_atr_stop  = _mask(c3_atr_stop_f)

    # Build shared full→display index map (used for both stop signal sets)
    mask_vals    = mask.values
    full_to_disp = {}
    disp_idx_map = 0
    for fi, mv in enumerate(mask_vals):
        if mv:
            full_to_disp[fi] = disp_idx_map
            disp_idx_map += 1

    def _build_stop_cd(meta_list):
        """Remap a list of stop meta dicts to display-frame bar indices."""
        out = []
        for m in meta_list:
            sb = m['stop_bar']
            if sb not in full_to_disp: continue
            out.append(dict(
                disp_bar    = full_to_disp[sb],
                entry_price = m['entry_price'],
                stop_level  = m['stop_level'],
                peak_pct    = m['peak_pct'],
                atr_mult    = m.get('atr_mult', atr_stop_mult),
                exit_type   = m.get('exit_type', 'atr_stop'),
            ))
        return out

    atr_stop_cd    = _build_stop_cd(atr_stop_meta)
    c3_atr_stop_cd = _build_stop_cd(c3_atr_stop_meta)

    def remap_patterns(patterns_full):
        mask_vals    = mask.values
        full_to_disp = {}
        disp_idx = 0
        for fi, mv in enumerate(mask_vals):
            if mv:
                full_to_disp[fi] = disp_idx
                disp_idx += 1
        out = []
        for p in patterns_full:
            bk = p['breakout_bar']
            if bk not in full_to_disp: continue
            pp = dict(p)
            pp['breakout_bar'] = full_to_disp[bk]
            pp['l1_bar']       = full_to_disp.get(p['l1_bar'], None)
            pp['l2_bar']       = full_to_disp.get(p['l2_bar'], None)
            if pp['l1_bar'] is None or pp['l2_bar'] is None: continue
            out.append(pp)
        return out

    vis_bull = remap_patterns(c3_bull_patterns_f) if show_c3 else []
    vis_bear = remap_patterns(c3_bear_patterns_f) if show_c3 else []

    full_masked = full[mask].reset_index(drop=True)
    green_cd = build_sr_customdata(sb_green, full_masked, cfg, 'green') if sb_green is not None else []
    red_cd   = build_sr_customdata(sb_red,   full_masked, cfg, 'red')   if sb_red   is not None else []
    c3_bull_cd = build_sr_customdata(c3_bull, full_masked, cfg, 'green') if c3_bull is not None else []
    c3_bear_cd = build_sr_customdata(c3_bear, full_masked, cfg, 'red')   if c3_bear is not None else []

    # ── Figure layout ─────────────────────────────────────────────────────────
    n_rows  = 3 if show_surge else 2
    heights = [0.75, 0.15, 0.10] if show_surge else [0.80, 0.20]
    specs   = [[{"secondary_y": True}]] + [[{"secondary_y": False}]] * (n_rows - 1)
    fig = make_subplots(rows=n_rows, cols=1, row_heights=heights,
                        shared_xaxes=True, vertical_spacing=0.025, specs=specs)

    # ── Candlesticks ──────────────────────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=sd['Date'], open=sd['open'], high=sd['high'], low=sd['low'], close=sd['close'],
        name='Price',
        increasing=dict(line=dict(color='#26A69A', width=1), fillcolor='#26A69A'),
        decreasing=dict(line=dict(color='#EF5350', width=1), fillcolor='#EF5350'),
        whiskerwidth=0,
    ), row=1, col=1, secondary_y=False)

    if show_ma_fast:
        fig.add_trace(go.Scatter(x=sd['Date'], y=ma['MA_fast'], mode='lines',
            name=cfg['ma_fast_label'], line=MA_STYLE['fast']), row=1, col=1, secondary_y=False)
    if show_ma_slow:
        fig.add_trace(go.Scatter(x=sd['Date'], y=ma['MA_slow'], mode='lines',
            name=cfg['ma_slow_label'], line=MA_STYLE['slow']), row=1, col=1, secondary_y=False)

    if sel_overlays:
        pv = sd['close'].dropna()
        for ind in sel_overlays:
            if ind not in cs.columns: continue
            raw = cs[ind].copy()
            fig.add_trace(go.Scatter(
                x=sd['Date'], y=scale_to_price(raw, pv), mode='lines',
                name=f'{ind} score', line=dict(width=1.0, color=OVERLAY_COLORS[ind], dash='dot'),
                opacity=0.80, hovertemplate=f'<b>{ind}</b>: %{{customdata:.1f}}<extra></extra>',
                customdata=raw,
            ), row=1, col=1, secondary_y=False)

    bar_clr = ['#26A69A' if sd['close'].iloc[i] >= sd['open'].iloc[i] else '#EF5350'
               for i in range(len(sd))]
    fig.add_trace(go.Bar(x=sd['Date'], y=sd['volume_usd'], name=cfg['vol_label'],
        marker=dict(color=bar_clr, line=dict(width=0)), opacity=0.15,
    ), row=1, col=1, secondary_y=True)

    # ── C3 drawings ───────────────────────────────────────────────────────────
    if show_c3:
        dates_arr = sd['Date'].values
        add_c3_pattern_shapes(fig, dates_arr, sd['close'].values.astype(float),
                              sd['low'].values.astype(float), sd['high'].values.astype(float),
                              vis_bull, row=1)
        add_c3_pattern_shapes(fig, dates_arr, sd['close'].values.astype(float),
                              sd['low'].values.astype(float), sd['high'].values.astype(float),
                              vis_bear, row=1)

    # ── C3 diamonds ───────────────────────────────────────────────────────────
    HTPL_C3 = (
        '%{customdata[4]}<br>Neckline: $%{customdata[5]}<br>'
        '─────────────────<br>'
        '<b>Support:</b> %{customdata[0]}<br><b>Resistance:</b> %{customdata[1]}<br>'
        '─────────────────<br>%{customdata[2]}<br><i>%{customdata[3]}</i><extra></extra>'
    )
    def _plot_c3(c3_sig, c3_conf, c3_fail, c3_cd, pats, is_bull):
        if c3_sig is None or not c3_sig.any(): return
        color_conf    = '#00BFA5' if is_bull else '#FF6D00'
        color_fail    = 'rgba(150,150,150,0.25)'
        direction_txt = "Double Bottom ◇" if is_bull else "Double Top ◇"
        neck_map      = {p['breakout_bar']: p['neckline'] for p in pats}
        all_idx       = c3_sig[c3_sig].index.tolist()
        cd_base       = [[t[0],t[1],t[2]] for t in c3_cd] if c3_cd else [['','','']]*len(all_idx)
        conf_mask_v   = c3_conf.iloc[all_idx].values if c3_conf is not None else np.ones(len(all_idx), bool)
        fail_mask_v   = c3_fail.iloc[all_idx].values if c3_fail is not None else np.zeros(len(all_idx), bool)
        conf_idx      = [i for i, m in zip(all_idx, conf_mask_v) if m]
        fail_idx      = [i for i, m in zip(all_idx, fail_mask_v) if m]

        def make_cd(idx_list):
            res = []
            for i in idx_list:
                base = cd_base[all_idx.index(i)] if i in all_idx else ['','','']
                neck = neck_map.get(i, 0)
                lbl  = f"✅ ≥{min_move_pct:.0f}% in {fwd_window}{bl[0]}" if i in conf_idx \
                       else f"❌ <{min_move_pct:.0f}% in {fwd_window}{bl[0]}"
                res.append([base[0], base[1], base[2], lbl, direction_txt, f"{neck:.4g}"])
            return res

        if conf_idx:
            y_pos = (sd['low'].iloc[conf_idx] * 0.992 if is_bull else sd['high'].iloc[conf_idx] * 1.008)
            add_pulse_halos(fig, sd['Date'].iloc[conf_idx], y_pos, color_conf)
            fig.add_trace(go.Scatter(
                x=sd['Date'].iloc[conf_idx], y=y_pos, mode='markers',
                name=f'C3 {direction_txt} confirmed',
                marker=dict(symbol='diamond', size=11, color=color_conf, line=dict(width=1.5, color='white')),
                customdata=make_cd(conf_idx),
                hovertemplate=f'<b>C3 {direction_txt} — CONFIRMED</b><br>' + HTPL_C3,
            ), row=1, col=1, secondary_y=False)
        if fail_idx:
            y_pos = (sd['low'].iloc[fail_idx] * 0.992 if is_bull else sd['high'].iloc[fail_idx] * 1.008)
            fig.add_trace(go.Scatter(
                x=sd['Date'].iloc[fail_idx], y=y_pos, mode='markers',
                name=f'C3 {direction_txt} weak',
                marker=dict(symbol='diamond', size=9, color=color_fail,
                            line=dict(width=1.2, color='rgba(150,150,150,0.35)')),
                customdata=make_cd(fail_idx),
                hovertemplate=f'<b>C3 {direction_txt} — WEAK</b><br>' + HTPL_C3,
            ), row=1, col=1, secondary_y=False)

    _plot_c3(c3_bull, c3_bull_conf, c3_bull_fail, c3_bull_cd, vis_bull, True)
    _plot_c3(c3_bear, c3_bear_conf, c3_bear_fail, c3_bear_cd, vis_bear, False)

    # ── C1/C2 entry / exit diamonds ───────────────────────────────────────────
    def _plot_c12(sb_sig, conf, fail, cd_list, is_entry):
        if sb_sig is None or not sb_sig.any(): return
        color_conf = '#00E676' if is_entry else '#FF1744'
        htpl_top   = cfg['entry_htpl_top'] if is_entry else cfg['exit_htpl_top']
        label_base = 'C1/C2 Entry ◇' if is_entry else 'C1/C2 Exit ◇'
        y_mult_conf = 0.995 if is_entry else 1.005
        y_src       = 'low'  if is_entry else 'high'

        all_idx   = sb_sig[sb_sig].index
        cd_all    = [[t[0],t[1],t[2]] for t in cd_list] if cd_list else [['','','']]*len(all_idx)
        conf_mask_v = conf.iloc[all_idx].values if conf is not None else np.ones(len(all_idx), dtype=bool)
        fail_mask_v = fail.iloc[all_idx].values if fail is not None else np.zeros(len(all_idx), dtype=bool)
        conf_idx  = [i for i, m in zip(all_idx, conf_mask_v) if m]
        fail_idx  = [i for i, m in zip(all_idx, fail_mask_v) if m]

        htpl = (htpl_top +
            '─────────────────<br>'
            '<b>Support:</b> %{customdata[0]}<br><b>Resistance:</b> %{customdata[1]}<br>'
            '─────────────────<br>%{customdata[2]}<br><i>%{customdata[3]}</i><extra></extra>')

        if conf_idx:
            y_pos = sd[y_src].iloc[conf_idx] * y_mult_conf
            cd    = [[*cd_all[list(all_idx).index(i)],
                      f"✅ Confirmed ≥{min_move_pct:.0f}% in {fwd_window}{bl[0]}"] for i in conf_idx]
            add_pulse_halos(fig, sd['Date'].iloc[conf_idx], y_pos, color_conf)
            fig.add_trace(go.Scatter(
                x=sd['Date'].iloc[conf_idx], y=y_pos, mode='markers',
                name=f'{label_base} confirmed (≥{min_move_pct:.0f}%)',
                marker=dict(symbol='diamond-open', size=12, color=color_conf,
                            line=dict(width=2.0, color=color_conf)),
                customdata=cd,
                hovertemplate=f'<b>{label_base} — CONFIRMED</b><br>' + htpl,
            ), row=1, col=1, secondary_y=False)
        if fail_idx:
            y_pos = sd[y_src].iloc[fail_idx] * y_mult_conf
            cd    = [[*cd_all[list(all_idx).index(i)],
                      f"❌ Did not reach {min_move_pct:.0f}% in {fwd_window}{bl[0]}"] for i in fail_idx]
            fig.add_trace(go.Scatter(
                x=sd['Date'].iloc[fail_idx], y=y_pos, mode='markers',
                name=f'{label_base} weak (dim)',
                marker=dict(symbol='diamond-open', size=10, color='rgba(150,150,150,0.25)',
                            line=dict(width=1.2, color='rgba(150,150,150,0.35)')),
                customdata=cd,
                hovertemplate=f'<b>{label_base} — WEAK</b><br>' + htpl,
            ), row=1, col=1, secondary_y=False)

    _plot_c12(sb_green, green_conf, green_fail, green_cd, True)
    _plot_c12(sb_red,   red_conf,   red_fail,   red_cd,   False)

    # ── ATR Stop-hit diamonds — shared plot helper ────────────────────────────
    def _plot_atr_stop(stop_cd, source_label):
        """
        Plot exit diamonds for any signal source.
        Colour and label differ by exit_type:
          ma_cross → orange  ◆  (MA cross fired first)
          atr_stop → bright red ◆  (hard ATR stop)
          both     → bright red ◆  (same bar)
        """
        if not stop_cd: return
        valid = [m for m in stop_cd if m['disp_bar'] < len(sd)]
        if not valid: return

        # Split by exit type for distinct visual treatment
        type_cfg = {
            'ma_cross': dict(color='#FF6D00', label='MA Cross Exit',  emoji='🟠'),
            'atr_stop': dict(color='#FF1744', label='ATR Stop Hit',   emoji='🔴'),
            'both':     dict(color='#FF1744', label='ATR+MA Exit',    emoji='🔴'),
        }

        groups = {}
        for m in valid:
            et = m.get('exit_type', 'atr_stop')
            groups.setdefault(et, []).append(m)

        for et, items in groups.items():
            tc   = type_cfg.get(et, type_cfg['atr_stop'])
            color = tc['color']
            idxs  = [m['disp_bar'] for m in items]
            y_pos = sd['high'].iloc[idxs] * 1.012

            exit_desc = {
                'ma_cross': f'Close crossed below MA{cfg["ma_fast"]} (early exit)',
                'atr_stop': f'Low hit ATR stop ({items[0]["atr_mult"]:.1f}× ATR below entry)',
                'both':     f'MA cross + ATR stop fired on same bar',
            }.get(et, '')

            cd = [[
                f"${m['entry_price']:.4g}",
                f"${m['stop_level']:.4g}",
                f"+{m['peak_pct']:.1f}% peak before exit",
                exit_desc,
            ] for m in items]

            # Glow rings
            for size, op in [(28, 0.45), (20, 0.65), (13, 0.85)]:
                fig.add_trace(go.Scatter(
                    x=sd['Date'].iloc[idxs], y=y_pos,
                    mode='markers', showlegend=False, hoverinfo='skip',
                    marker=dict(symbol='diamond', size=size,
                                color='rgba(0,0,0,0)',
                                line=dict(width=2, color=color),
                                opacity=op),
                ), row=1, col=1, secondary_y=False)

            fig.add_trace(go.Scatter(
                x=sd['Date'].iloc[idxs], y=y_pos,
                mode='markers',
                name=f'{tc["emoji"]} {source_label} {tc["label"]} (after +{atr_stop_profit_pct:.0f}%)',
                marker=dict(symbol='diamond', size=14, color=color,
                            line=dict(width=2, color='#FFFFFF')),
                customdata=cd,
                hovertemplate=(
                    f'<b>{tc["emoji"]} {source_label} — {tc["label"].upper()}</b><br>'
                    '─────────────────<br>'
                    'Entry price : $%{customdata[0]}<br>'
                    'Stop level  : $%{customdata[1]}<br>'
                    '─────────────────<br>'
                    '%{customdata[2]}<br>'
                    '<i>%{customdata[3]}</i>'
                    '<extra></extra>'
                ),
            ), row=1, col=1, secondary_y=False)

    if show_atr_stop:
        _plot_atr_stop(atr_stop_cd,    'C1/C2')
        _plot_atr_stop(c3_atr_stop_cd, 'C3')

    # ── Score panel ───────────────────────────────────────────────────────────
    for yv, clr, ds in [(90,'#6A1B9A','dash'),(10,'#C62828','dashdot'),(50,'#cccccc','dot')]:
        fig.add_hline(y=yv, line_dash=ds, line_color=clr, opacity=0.40, row=2, col=1)
    score_lbl = f"{cfg['pct_rank_win']}{bl[0]}%"
    for cat_name, show in [('Structure',show_str),('Momentum',show_mom),('Volatility',show_vol_score)]:
        if not show or cat_name not in p_f.columns: continue
        y_disp = smooth(p_f[cat_name], smooth_window)
        fig.add_trace(go.Scatter(x=sd['Date'], y=y_disp, mode='lines',
            name=f'{cat_name} {score_lbl}', line=SCORE_STYLE[cat_name], opacity=0.92), row=2, col=1)
        if cat_name == 'Volatility':
            fig.add_trace(go.Scatter(
                x=pd.concat([sd['Date'], sd['Date'][::-1]]),
                y=pd.concat([y_disp.clip(lower=90), pd.Series([90]*len(sd), index=sd.index)]),
                fill='toself', fillcolor='rgba(106,27,154,0.08)',
                line=dict(width=0), showlegend=False, hoverinfo='skip',
            ), row=2, col=1)

    # ── Surge panel ───────────────────────────────────────────────────────────
    if show_surge and s_sc is not None:
        fig.add_hrect(y0=surge_thr, y1=500, fillcolor="rgba(0,200,83,0.06)", layer="below", line_width=0, row=3, col=1)
        fig.add_hrect(y0=-500, y1=-surge_thr, fillcolor="rgba(211,47,47,0.06)", layer="below", line_width=0, row=3, col=1)
        fig.add_hline(y=surge_thr,  line_dash="dash",  line_color="#00C853", opacity=0.5, row=3, col=1)
        fig.add_hline(y=-surge_thr, line_dash="dash",  line_color="#D32F2F", opacity=0.5, row=3, col=1)
        fig.add_hline(y=0,          line_dash="solid", line_color="#aaaaaa", opacity=0.4, row=3, col=1)
        fig.add_trace(go.Scatter(x=sd['Date'], y=s_sc, mode='lines', name='Surge',
            line=dict(width=1.6, color='#E91E63'), fill='tozeroy',
            fillcolor='rgba(233,30,99,0.07)'), row=3, col=1)
        up_i   = s_sg[s_sg ==  1].index
        down_i = s_sg[s_sg == -1].index
        if len(up_i):
            fig.add_trace(go.Scatter(x=sd['Date'].iloc[up_i], y=s_sc.iloc[up_i],
                mode='markers', name='🚀 Surge up',
                marker=dict(size=9, color='#00C853', symbol='triangle-up',
                            line=dict(width=1.5, color='white'))), row=3, col=1)
        if len(down_i):
            fig.add_trace(go.Scatter(x=sd['Date'].iloc[down_i], y=s_sc.iloc[down_i],
                mode='markers', name='💥 Surge down',
                marker=dict(size=9, color='#D32F2F', symbol='triangle-down',
                            line=dict(width=1.5, color='white'))), row=3, col=1)

    # ── Layout ────────────────────────────────────────────────────────────────
    fig.update_layout(
        hovermode='x unified', template='plotly_dark', height=880,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=10, color='#9B9EA4'), bgcolor='rgba(0,0,0,0)', borderwidth=0),
        plot_bgcolor='#0D1117', paper_bgcolor='#0D1117',
        font=dict(color='#9B9EA4', family='Helvetica Neue, Arial'),
        margin=dict(l=64, r=64, t=36, b=36),
        bargap=0, xaxis_rangeslider_visible=False,
        hoverlabel=dict(bgcolor='#1C2128', bordercolor='#30363D',
                        font=dict(size=12, color='#E8E9EA', family='Helvetica Neue, Arial')),
    )
    xax = dict(showgrid=True, gridcolor='#161B22', gridwidth=1, zeroline=False,
               tickfont=dict(color='#6E7681', size=10), tickcolor='#30363D', linecolor='#30363D',
               showspikes=True, spikemode='across', spikesnap='cursor',
               spikecolor='#58A6FF', spikethickness=1, spikedash='dot')
    yax = dict(gridcolor='#161B22', zeroline=False,
               tickfont=dict(color='#6E7681', size=10), tickcolor='#30363D', linecolor='#30363D')
    for r in range(1, n_rows + 1):
        fig.update_xaxes(**xax, row=r, col=1)
    fig.update_xaxes(title_text=cfg['x_title'], row=n_rows, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1, secondary_y=False, **yax,
                     showspikes=True, spikecolor='#787B86', spikethickness=1,
                     spikedash='solid', spikemode='across')
    fig.update_yaxes(title_text="Vol", row=1, col=1, secondary_y=True,
                     showgrid=False, tickfont=dict(size=8, color='#555a67'))
    fig.update_yaxes(title_text=cfg['score_label'], range=[0,105],
                     tickvals=[0,10,50,90,100], row=2, col=1, **yax)
    if show_surge:
        fig.update_yaxes(title_text=cfg['surge_label_ax'], row=3, col=1,
                         gridcolor='#161B22', zeroline=True, zerolinecolor='#30363D',
                         tickfont=dict(color='#787B86', size=10))

    return fig, s_sc, s_sg, vis_bull, vis_bear


# ════════════════════════════════════════════════════════════════════════════════
# APP
# ════════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: #0D1117 !important;
    border-right: 1px solid #21262D;
    padding-top: 0 !important;
}
.sb-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 12px 14px 10px;
    margin: 0 0 10px 0;
}
.sb-card-title {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #58A6FF;
    margin-bottom: 10px;
}
.coin-badge {
    background: #1C2128;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 10px 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 8px;
}
[data-testid="stSidebarContent"] { padding-top: 1rem; }
[data-testid="stSidebar"] .stCheckbox { margin-bottom: 2px; }
[data-testid="stSidebar"] .stSlider   { margin-bottom: 4px; }
.tf-badge-daily   { color: #26A69A; font-size:13px; font-weight:500; }
.tf-badge-weekly  { color: #58A6FF; font-size:13px; font-weight:500; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Timeframe toggle (top of sidebar) ─────────────────────────────────────
    st.markdown('<div class="sb-card"><div class="sb-card-title">⏱ Timeframe</div>', unsafe_allow_html=True)
    timeframe = st.radio("", ["Daily", "Weekly"], horizontal=True, label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    cfg = TIMEFRAME_CFG[timeframe]
    bl  = cfg['bar_label']

    # Load data for selected timeframe
    df, symbols = load_data(cfg['csv_path'])

    # ── Coin selector ──────────────────────────────────────────────────────────
    st.markdown('<div class="sb-card"><div class="sb-card-title">🔍 Select Coin</div>', unsafe_allow_html=True)
    srch = st.text_input("", "", placeholder="Search: BTC, ETH, SOL…", label_visibility="collapsed")
    fsym = [s for s in symbols if srch.upper() in s.upper()] if srch else symbols
    sym_list = fsym or symbols

    # Restore previously selected symbol when toggling timeframes.
    # If the symbol exists in the new list, jump straight to it.
    # If it's missing (coin absent from weekly CSV), fall back to index 0.
    prev        = st.session_state.get("selected_symbol", sym_list[0])
    default_idx = sym_list.index(prev) if prev in sym_list else 0

    selected_symbol = st.selectbox(
        "", sym_list,
        index=default_idx,
        label_visibility="collapsed",
        key="selected_symbol",   # writes choice back to session_state automatically
    )

    coin_row  = df[df['symbol'] == selected_symbol].iloc[-1]
    mcap      = coin_row.get('market_cap_usd', None)
    mcap_str  = f"${mcap/1e9:.2f}B" if mcap and mcap >= 1e9 else (f"${mcap/1e6:.0f}M" if mcap else "—")
    tier      = str(coin_row.get('cap_tier', '—')).capitalize()
    price_val = float(coin_row.get('close', coin_row.get('price_usd', 0)) or 0)
    chg       = float(coin_row.get('change_24h_pct', 0) or 0)
    chg_col   = "#26A69A" if chg >= 0 else "#EF5350"
    chg_sym   = "▲" if chg >= 0 else "▼"
    tf_badge  = f"<span style='font-size:10px;color:#58A6FF;margin-left:4px'>{timeframe}</span>"
    st.markdown(f"""
    <div class="coin-badge">
      <div>
        <div style="font-size:17px;font-weight:700;color:#E8E9EA;line-height:1.2">
          {selected_symbol}{tf_badge}
        </div>
        <div style="font-size:11px;color:#8B949E;margin-top:2px">{tier} cap &nbsp;·&nbsp; {mcap_str}</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:15px;font-weight:600;color:#E8E9EA;line-height:1.2">${price_val:.4g}</div>
        <div style="font-size:12px;color:{chg_col};margin-top:2px">{chg_sym} {abs(chg):.2f}%</div>
      </div>
    </div></div>
    """, unsafe_allow_html=True)

    # ── C1/C2 Signals ─────────────────────────────────────────────────────────
    st.markdown(f'<div class="sb-card"><div class="sb-card-title">⚡ C1 / C2 Signals ({timeframe})</div>', unsafe_allow_html=True)
    show_sb = st.checkbox("C1 / C2 signal markers", value=True, help=cfg['c1_desc'])
    if show_sb:
        st.caption("Signal quality filter")
        _fq1, _fq2 = st.columns(2)
        min_move_pct = _fq1.slider("Min move %", 1.0, 20.0, cfg['def_min_move'], step=0.5 if timeframe == "Daily" else 1.0)
        fwd_window   = _fq2.slider(cfg['fwd_label'], 2 if timeframe == "Weekly" else 3, 12 if timeframe == "Weekly" else 30, cfg['def_fwd_window'])
    else:
        min_move_pct = cfg['def_min_move']; fwd_window = cfg['def_fwd_window']

    st.caption("False signal filters")
    _fg1, _fg2 = st.columns(2)
    c12_vol_spike  = _fg1.checkbox("Vol spike",    value=True)
    c12_rsi_filter = _fg2.checkbox("RSI oversold", value=False)
    c12_vol_mult   = st.slider("Vol multiplier", 1.0, 4.0, 1.5, step=0.25, disabled=not c12_vol_spike)
    c12_rsi_max    = st.slider("RSI max", 20, 55, 40) if c12_rsi_filter else 40.0
    _fg3, _fg4 = st.columns(2)
    c12_adx_filter    = _fg3.checkbox("ADX weak",               value=False)
    c12_ma_slow_filter= _fg4.checkbox(f"Above {cfg['ma_slow_label']}", value=False)
    c12_adx_max       = st.slider("ADX max", 15, 40, 25) if c12_adx_filter else 25.0

    st.markdown(
        "<div style='border-top:1px solid #21262D;margin:8px 0 6px'></div>"
        "<span style='font-size:10px;font-weight:700;letter-spacing:0.08em;"
        "text-transform:uppercase;color:#26A69A'>🟢 Positive Trend Gate</span>",
        unsafe_allow_html=True,
    )
    c12_trend_filter = st.checkbox(
        "Only show pullbacks in uptrend",
        value=True,
        help=(
            "Only show green entry diamonds when price is above both MAs\n"
            "(momentum washout while holding above MA = healthy pullback).\n\n"
            "MA check (primary — always applied when enabled):\n"
            f"  close > {cfg['ma_fast_label']}  +1 pt\n"
            f"  close > {cfg['ma_slow_label']}  +1 pt\n"
            "  → Require BOTH = min MA score of 2\n\n"
            "Extended check (optional, adds structure context):\n"
            f"  {cfg['ma_fast_label']} > {cfg['ma_slow_label']} (golden cross zone)  +1\n"
            "  Supertrend bullish  +1\n"
            "  EMA 50 slope rising  +1\n"
            "  → Set Min extra score = 0 to ignore these"
        ),
    )
    if c12_trend_filter:
        st.caption("MA gate (primary)")
        c12_trend_min_ma_score = st.slider(
            f"Must be above both MAs",
            min_value=0, max_value=2, value=2,
            help=(
                f"2 = must be above BOTH {cfg['ma_fast_label']} and {cfg['ma_slow_label']}  ← recommended\n"
                f"1 = above at least one MA\n"
                "0 = MA check disabled"
            ),
        )
        st.caption("Extended trend structure (optional)")
        c12_trend_min_full_score = st.slider(
            "Min extra score (0 = off)",
            min_value=0, max_value=5, value=0,
            help=(
                "0 = only check MAs (recommended — Supertrend/EMA slope\n"
                "    are often suppressed during the very pullback C1/C2 targets)\n"
                "3+ = also require golden cross + Supertrend + EMA slope"
            ),
        )
    else:
        c12_trend_min_ma_score   = 0
        c12_trend_min_full_score = 0
    st.markdown("</div>", unsafe_allow_html=True)

    # ── C3 ─────────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="sb-card"><div class="sb-card-title">🔶 C3 Double Bottom / Top ({timeframe})</div>', unsafe_allow_html=True)
    show_c3 = st.checkbox("Detect double patterns", value=True)
    if show_c3:
        st.caption(f"Parameters (in {bl})")
        _ca1, _ca2 = st.columns(2)
        c3_order     = _ca1.slider(f"Swing order ({bl[0]})", 2, 8, cfg['def_c3_order'])
        c3_price_tol = _ca2.slider("Price tol %", 1, 10, 4)
        _cb1, _cb2 = st.columns(2)
        c3_min_sep  = _cb1.slider(f"Min gap ({bl})", 2, 30, cfg['def_c3_min_sep'])
        c3_max_bars = _cb2.slider(f"Max lookback ({bl})", 10, 300 if timeframe == "Daily" else 104, cfg['def_c3_max_bars'])
        c3_neck_wait    = st.slider(f"Neckline wait ({bl})", 2, 60 if timeframe == "Daily" else 20, cfg['def_c3_neck_wait'])
        c3_min_magnitude= st.slider("Min magnitude %", 1, 30, cfg['def_c3_min_mag'])
    else:
        c3_order=cfg['def_c3_order']; c3_price_tol=4
        c3_min_sep=cfg['def_c3_min_sep']; c3_max_bars=cfg['def_c3_max_bars']
        c3_neck_wait=cfg['def_c3_neck_wait']; c3_min_magnitude=cfg['def_c3_min_mag']
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Price overlays ─────────────────────────────────────────────────────────
    st.markdown('<div class="sb-card"><div class="sb-card-title">📈 Price Overlays</div>', unsafe_allow_html=True)
    sel_overlays = st.multiselect("", list(OVERLAY_COLORS.keys()), default=[], label_visibility="collapsed",
                                  placeholder="Add category score overlay…")
    _oc1, _oc2 = st.columns(2)
    show_ma_fast = _oc1.checkbox(cfg['ma_fast_label'], value=True)
    show_ma_slow = _oc2.checkbox(cfg['ma_slow_label'], value=False)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Score panel ────────────────────────────────────────────────────────────
    st.markdown(f'<div class="sb-card"><div class="sb-card-title">📊 Score Panel ({cfg["pct_rank_win"]}{bl[0]} %ile)</div>', unsafe_allow_html=True)
    _sc1, _sc2, _sc3 = st.columns(3)
    show_str       = _sc1.checkbox("Struct", value=True)
    show_mom       = _sc2.checkbox("Mom",    value=True)
    show_vol_score = _sc3.checkbox("Vol",    value=True)
    smooth_window  = st.slider("Smoothing", 1, cfg['smooth_max'], cfg['smooth_def'])
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Surge ──────────────────────────────────────────────────────────────────
    st.markdown(f'<div class="sb-card"><div class="sb-card-title">🚀 Surge Score ({timeframe})</div>', unsafe_allow_html=True)
    show_surge = st.checkbox("Show surge panel", value=True)
    if show_surge:
        _su1, _su2 = st.columns(2)
        surge_lb  = _su1.slider(f"Lookback ({bl[0]})", 2, 5, cfg['def_surge_lb'])
        surge_thr = _su2.slider("Threshold", 5, 30, 10)
    else:
        surge_lb = cfg['def_surge_lb']; surge_thr = 10
    st.markdown("</div>", unsafe_allow_html=True)   # close surge card

    # ── ATR Stop Signal ────────────────────────────────────────────────────────
    st.markdown('<div class="sb-card"><div class="sb-card-title">🔴 ATR Stop-Loss Signal</div>', unsafe_allow_html=True)
    show_atr_stop = st.checkbox(
        "Show ATR stop-hit signal",
        value=True,
        help=(
            "After a green entry moves ≥ Profit threshold %, monitors for the\n"
            "first bar whose LOW touches entry_close − N×ATR.\n"
            "Fires a bright red ◆ at that bar as a take-profit / exit alert.\n\n"
            "Only entries that actually hit the profit target are watched —\n"
            "failed entries are ignored entirely."
        ),
    )
    if show_atr_stop:
        _as1, _as2 = st.columns(2)
        atr_stop_profit_pct = _as1.slider(
            "Profit gate %", 5, 100, 20, step=5,
            help="Entry must reach this % gain before the stop is armed",
        )
        atr_stop_mult = _as2.slider(
            "ATR multiplier", 0.5, 4.0, 1.5, step=0.25,
            help="Stop level = entry_close − N × ATR(entry bar)",
        )
    else:
        atr_stop_profit_pct = 20.0
        atr_stop_mult       = 1.5
    st.markdown("</div>", unsafe_allow_html=True)
tf_color  = "#26A69A" if timeframe == "Daily" else "#58A6FF"
tf_dot    = "●"
st.markdown(
    f"<h2 style='margin:0 0 2px;color:#E8E9EA;font-family:Helvetica Neue,Arial;font-weight:600'>"
    f"₿ Crypto Chart Viewer &nbsp;"
    f"<span style='font-size:14px;color:{tf_color};font-weight:500'>{tf_dot} {timeframe}</span></h2>"
    f"<p style='margin:0 0 18px;color:#8B949E;font-size:13px;letter-spacing:0.03em'>"
    f"C1 · C2 · C3 signals &nbsp;|&nbsp; Surge score &nbsp;|&nbsp; S/R levels &nbsp;|&nbsp; {timeframe.lower()} bars</p>",
    unsafe_allow_html=True,
)

# ── Date range ────────────────────────────────────────────────────────────────
full = df[df['symbol'] == selected_symbol].copy().sort_values('Date').reset_index(drop=True)
mn, mx = full['Date'].min().date(), full['Date'].max().date()
default_start = max(mn, mx - timedelta(days=cfg['default_range_days']))

_dc1, _dc2 = st.columns(2)
with _dc1:
    d0 = st.date_input("From", value=default_start, min_value=mn, max_value=mx)
with _dc2:
    d1 = st.date_input("To",   value=mx,            min_value=mn, max_value=mx)

# ── Render ────────────────────────────────────────────────────────────────────
has_data = full[(full['Date'].dt.date >= d0) & (full['Date'].dt.date <= d1)]
if len(has_data) < cfg['min_bars']:
    st.warning(f"Not enough {bl} in range — try widening the window (need at least {cfg['min_bars']} {bl}).")
else:
    with st.spinner(f"Calculating {timeframe.lower()} signals…"):
        fig, s_sc, s_sg, bull_pats, bear_pats = create_chart(
            full, cfg, selected_symbol, sel_overlays,
            show_surge, surge_lb, surge_thr,
            d0, d1,
            show_ma_fast, show_ma_slow,
            show_str, show_mom, show_vol_score, smooth_window,
            show_sb, fwd_window, min_move_pct,
            show_c3, c3_order, c3_min_sep, c3_max_bars,
            c3_price_tol / 100.0,
            c3_neck_wait,
            c3_min_magnitude / 100.0,
            c12_vol_spike, c12_vol_mult,
            c12_rsi_filter, c12_rsi_max,
            c12_adx_filter, c12_adx_max,
            c12_ma_slow_filter,
            c12_trend_filter=c12_trend_filter,
            c12_trend_min_ma_score=c12_trend_min_ma_score,
            c12_trend_min_full_score=c12_trend_min_full_score,
            show_atr_stop=show_atr_stop,
            atr_stop_profit_pct=atr_stop_profit_pct,
            atr_stop_mult=atr_stop_mult,
        )
    st.plotly_chart(fig, use_container_width=True)

    # ── C3 pattern table ───────────────────────────────────────────────────────
    if show_c3 and (bull_pats or bear_pats):
        st.markdown("---")
        st.subheader(f"📐 C3 Double Patterns (visible window)")
        rows = []
        for p in sorted(bull_pats + bear_pats, key=lambda x: x['breakout_bar']):
            dates_disp = has_data.reset_index(drop=True)
            bk = p['breakout_bar']
            if bk >= len(dates_disp): continue
            rows.append({
                'Type':              '🟢 Double Bottom' if p['type'] == 'double_bottom' else '🔴 Double Top',
                f'Breakout ({bl[:-1]})': dates_disp.loc[bk, 'Date'].strftime('%Y-%m-%d'),
                'Level 1':           f"${p['l1_price']:.4g}",
                'Level 2':           f"${p['l2_price']:.4g}",
                'Neckline':          f"${p['neckline']:.4g}",
                f'Gap ({bl})':       p['l2_bar'] - p['l1_bar'],
            })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Surge events table ─────────────────────────────────────────────────────
    if show_surge and s_sg is not None:
        ev_idx = s_sg[s_sg != 0].tail(10).index
        if len(ev_idx) > 0:
            st.markdown("---")
            st.subheader(f"🚀 Recent {timeframe} Surge Events")
            sd_ev = full[(full['Date'].dt.date >= d0) &
                         (full['Date'].dt.date <= d1)].reset_index(drop=True)
            rows = []
            for i in ev_idx:
                lbl, _ = surge_label(s_sg.loc[i], s_sc.loc[i])
                rows.append({
                    'Date':  sd_ev.loc[i, 'Date'].strftime('%Y-%m-%d'),
                    'Event': lbl,
                    'Score': f"{s_sc.loc[i]:.1f}",
                    'Close': f"${sd_ev.loc[i, 'close']:.4g}",
                    'RSI':   f"{sd_ev.loc[i, 'RSI']:.1f}" if 'RSI' in sd_ev.columns else '—',
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Snapshot metrics ───────────────────────────────────────────────────────
    latest = full.iloc[-1]
    st.markdown("---")
    st.subheader(f"📋 Latest {timeframe} Snapshot")
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Price",       f"${float(latest['close']):.4g}")
    m2.metric("24h Change",  f"{float(latest.get('change_24h_pct', 0) or 0):.2f}%")
    m3.metric("RSI",         f"{float(latest.get('RSI', 0) or 0):.1f}")
    vol_val = float(latest.get('volume_usd', 0) or 0)
    m4.metric("Volume",      f"${vol_val/1e6:.1f}M" if timeframe == "Weekly" else f"{vol_val/1e6:.1f}M")
    m5.metric("ATR",         f"${float(latest.get('ATR', 0) or 0):.4g}")
    m6.metric("Surge Score", f"{float(latest.get('surge_score', 0) or 0):.2f}")