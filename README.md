# Crypto Similarity Analysis

## Overview
In cryptocurrency portfolio management, investors frequently rebalance or rotate capital between different crypto assets to optimize returns or manage risk. However, every transaction (buying, selling, swapping) incurs explicit costs (exchange fees, spreads, slippage, taxes) and implicit costs (execution risk, liquidity risk, timing risk).

This project addresses the following core question:

> **How can we identify and classify cryptocurrencies that exhibit similar performance behavior, so that unnecessary fund transfers between highly similar assets can be avoided?**

If two cryptocurrencies behave very similarly in terms of price dynamics, volatility structure, and risk-adjusted returns, reallocating capital from one to the other is unlikely to provide meaningful diversification or performance improvement—while still incurring transaction costs.

The goal is to systematically detect such similarities and group cryptocurrencies into clusters based on historical performance characteristics.



## Motivation

### Why This Matters
- **Transaction costs reduce net returns**  
  Frequent switching between behaviorally similar assets erodes portfolio performance over time.
- **False diversification**  
  Holding or rotating between highly correlated or structurally similar cryptos creates an illusion of diversification without real risk reduction.
- **Portfolio efficiency**  
  Investors often lack objective decision support to determine whether switching between assets is economically justified.

By classifying similar cryptocurrencies, investors can:
- Avoid redundant trades
- Reduce unnecessary portfolio churn
- Make more informed rebalancing and rotation decisions



## Objectives
- Measure similarity between cryptocurrencies based on historical performance characteristics.
- Classify or cluster cryptocurrencies into groups with statistically and economically similar behavior.
- Support portfolio decisions by flagging asset switches that are likely inefficient due to high similarity.

> **Note:**  
> This is **not a price-prediction system**, but a **decision-support framework** focused on minimizing unnecessary trading and improving portfolio efficiency.



## Scope of Similarity
Similarity is evaluated using performance-related characteristics such as:
- Returns (daily, weekly, monthly)
- Volatility and volatility regimes
- Maximum drawdowns and recovery patterns
- Risk-adjusted metrics (e.g., Sharpe, Sortino)
- Correlation and co-movement structures
- Time-series dynamics (trend persistence, regime shifts, tail behavior)

Two cryptocurrencies are considered similar if their performance metrics and time-series behavior are statistically and economically close over a defined time horizon.



## Universe Selection (Which Cryptos to Analyze)
Given the existence of ~14,000 cryptocurrencies, the project focuses on a filtered and economically meaningful universe.

Selection criteria include:
- **Liquidity**: Minimum trading volume and market depth
- **Market capitalization**: Exclusion of extremely small or illiquid tokens
- **Data availability**: Sufficient historical data for stable statistical analysis
- **Exchange coverage**: Assets listed on reputable exchanges
- **Continuity**: Avoidance of tokens with frequent halts or unreliable pricing
- **Economic relevance**: Representation across major crypto sectors (L1s, L2s, DeFi, infrastructure, payments)

This filtering ensures robustness and interpretability of similarity results.


## Key Assumption
If two cryptocurrencies belong to the same similarity cluster, reallocating capital between them is unlikely to materially improve portfolio performance **after accounting for transaction costs and execution frictions**.

This enables the system to recommend **“do not switch”** decisions unless assets belong to sufficiently different performance clusters.



## Expected Outcomes
- Clear grouping of cryptocurrencies based on performance similarity
- Quantitative similarity scores or cluster labels
- Actionable insights such as:
  - *“Asset A and Asset B are highly similar — switching is not cost-inefficient.”*
  - *“Asset C belongs to a different performance cluster — switching may improve diversification.”*



## Use Cases
- Crypto portfolio rebalancing strategies
- Fund rotation logic in algorithmic or systematic trading systems
- Research on crypto market structure and asset redundancy
- Decision support for medium- and long-term investors



## Non-Goals
This project does **not** aim to:
- Predict future crypto prices
- Provide financial advice
- Optimize exact trade timing

It focuses strictly on **similarity detection and classification** to reduce inefficient trading behavior.



## Summary
This project addresses a practical inefficiency in crypto investing: switching between assets that behave almost identically. By clustering cryptocurrencies based on performance similarity and restricting analysis to economically meaningful assets, the framework helps investors reduce unnecessary trades, minimize costs, and make more rational portfolio decisions.
