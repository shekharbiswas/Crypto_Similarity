# Crypto Similarity

In cryptocurrency portfolio management, investors frequently rebalance or rotate capital between different crypto assets to optimize returns or manage risk. 
However, every transaction (buying, selling, swapping) incurs **explicit costs** (exchange fees, spreads, slippage, taxes) and **implicit costs** (execution risk, timing risk).

The core problem addressed by this project is:

> **How can we identify and classify cryptocurrencies that exhibit similar performance behavior, so that unnecessary fund transfers between highly similar assets can be avoided?**

If two cryptocurrencies behave very similarly in terms of price movement, volatility, and risk-adjusted returns, moving funds from one to the other is unlikely to provide meaningful diversification or performance improvement, while still incurring transaction costs.

This project aims to systematically detect such similarities and group cryptocurrencies into clusters based on their historical performance characteristics.



## 2. Motivation

### Why this problem matters

* **Transaction costs reduce net returns**: Frequent switching between similar assets erodes profits.
* **False diversification**: Holding or switching between highly correlated or behaviorally similar cryptos gives an illusion of diversification without real risk reduction.
* **Portfolio efficiency**: Investors need decision support to determine *when switching assets is actually beneficial*.

By classifying similar cryptocurrencies, investors can:

* Avoid redundant trades
* Reduce churn in portfolios
* Make more informed rebalancing decisions


## 3. Objective


1. **Measure similarity** between cryptocurrencies based on historical performance.
2. **Classify or cluster** cryptocurrencies into groups with similar behavior.
3. **Support portfolio decisions** by flagging asset switches that are likely inefficient due to high similarity.

The output is **not a price prediction system**, but a **decision-support framework** focused on reducing unnecessary trading.
(TBA)



## 4. Scope of Similarity

Similarity is evaluated using performance-related characteristics, such as:

* Returns (daily, weekly, or monthly)
* Volatility
* Drawdowns
* Risk-adjusted metrics (e.g., Sharpe ratio)
* Correlation and co-movement patterns
* More

Two cryptocurrencies are considered *similar* if their performance metrics and time-series behavior are statistically and economically close over a given time horizon.


## 5. Key Assumption

> If two cryptocurrencies belong to the same similarity cluster, reallocating capital between them is unlikely to materially improve portfolio performance after accounting for transaction costs.

This assumption allows the system to recommend **"do not switch"** decisions unless assets belong to sufficiently different clusters.



## 6. Expected Outcome

* A clear grouping of cryptocurrencies based on performance similarity
* Quantitative similarity scores or cluster labels
* Actionable insights such as:

  * "Asset A and Asset B are highly similar — switching is not cost-effective"
  * "Asset C belongs to a different performance cluster — switching may provide diversification"



## 7. Intended Use Cases

* Crypto portfolio rebalancing strategies
* Fund rotation logic in algorithmic trading systems
* Research on crypto market structure and asset redundancy
* Decision support for long-term and medium-term investors


## 8. Non-Goals

This project does **not** aim to:

* Predict future crypto prices
* Provide financial advice
* Optimize exact trade timing

It focuses strictly on **similarity detection and classification** to reduce inefficient trading behavior.



## 9. Summary

This project addresses a practical and costly inefficiency in crypto investing: switching between assets that behave almost the same. 
By classifying cryptocurrencies based on performance similarity, the system helps investors minimize unnecessary trades, reduce costs, and make more rational portfolio decisions.
