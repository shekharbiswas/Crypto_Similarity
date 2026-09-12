# Crypto Intelligence Dashboard

## TL;DR 

- This is a Streamlit web app that shows charts and stats about many cryptocurrencies.
- It loads historical price/volume/indicator data and splits coins into 4 size groups: large, mid, small, micro.
- It has 6 tabs: Market Overview, Tier Breakdown, Coin Deep Dive, Return Similarity, Regime Similarity, and Forward Return Lab.
- Each tab answers a different question: How risky/profitable is a coin? Which coins move together? Which coins look technically alike today? What usually happens next?
- Every tab has a built-in explanation box in the app itself, right above its charts.

---

## Where to find the explanations in the app

Every tab has a light-gray/white info box at the top explaining what that tab does, in plain English. Look for this pattern in the code:

```
<div style='background:#ffffff;border:1px solid #cbd5e1; ... '>
<div style='color:#0077b6; ... '>◈ ...</div>
<div style='color:#475569; ... '>
   [explanation text here]
</div></div>
```

Search the file for `◈ How to read` or `◈ What this` to jump straight to each tab's explanation.

| Tab | Explanation box location (search text) |
|---|---|
| Market Overview | `◈ How to read this chart` |
| Tier Breakdown | `◈ Cap tier definitions` |
| Coin Deep Dive | `◈ How to read this tab` |
| Return Similarity | `◈ What this engine measures` |
| Regime Similarity | `◈ How regime similarity differs from return similarity` |
| Forward Return Lab | `◈ What this lab answers` |

---

## The 6 tabs

### 1. Market Overview
A bubble chart. Each bubble = one coin. Shows how risky (volatile) vs. how profitable each coin has been. Bigger bubble = bigger market cap.

### 2. Tier Breakdown
Groups coins into 4 size buckets (large, mid, small, micro) and compares average returns and volatility per group.

### 3. Coin Deep Dive
Pick one coin and see its price chart plus common technical indicators (RSI, MACD, volume) and a quick "current trend status" summary.

### 4. Return Similarity
Finds which coins have historically moved up/down on the same days as a chosen coin (correlation of daily returns).

### 5. Regime Similarity
Finds which coins are in a similar technical situation **right now** (not history) — same momentum, same trend state, etc.

### 6. Forward Return Lab
Looks back at every time a coin was in a similar technical state before, and shows what happened to its price in the days after — a "historical odds" check, not a prediction.

---

## Key concepts used

- **Cap tier**: coins are grouped by market cap size into 4 groups: large, mid, small, micro.
- **Volatility**: how much a coin's daily price swings around — higher = riskier.
- **Pearson correlation**: a score from -1 to 1 showing whether two coins tend to move up/down on the same days. Close to 1 = they move together.
- **Same-Dir %**: out of all shared days, how often did both coins move in the same direction (up or down)? A simple double-check on correlation.
- **Regime**: a coin's current technical "mood" — combining indicators like RSI, trend direction, and momentum into one snapshot.
- **Cosine similarity**: like Pearson correlation, but used to compare two coins' *current* technical readings instead of their price history.
- **Forward return**: what actually happened to the price 1–7 days after a certain condition was seen in the past — used to check historical odds, not to predict the future.

---

## Stats & methods used 

The app leans on a handful of statistical ideas to compare coins, and each one answers a slightly different question.

First, it measures **volatility** — basically how wildly a coin's price swings day to day. This is calculated as the standard deviation of daily returns, and it's used as the "risk" side of every risk-vs-return chart in the app.

Second, it uses **Pearson correlation** to check whether two coins have historically moved up and down on the same days. This is a score between -1 and 1: close to 1 means they tend to rise and fall together, close to 0 means no relationship, and negative means they tend to move opposite each other. This is the core method behind the Return Similarity tab.

Third, for checking whether coins are behaving alike *right now* (not historically), the app builds a small profile for each coin using indicators like RSI, ADX, Bollinger Band position, trend direction, and moving average alignment. It then compares these profiles using **cosine similarity**, which measures how closely two coins' current technical "shape" matches, regardless of scale.

Finally, for the Forward Return Lab, the app uses simple **historical averages (median returns)** — it looks back at every time a coin was in a similar technical state and checks what actually happened to its price afterward. This isn't a prediction model; it's closer to a "how did this play out historically" check, similar to a sports stat like a team's win rate in a certain situation.

## Important note on correlation vs. tiers

Pearson correlation is calculated across **all coins at once** — it is not calculated separately inside each tier group. The cap tier filter (sidebar) only **filters which results are shown afterward** — it does not change how the correlation itself is computed.