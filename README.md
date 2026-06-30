# India Risk Dashboard

A Python tool for risk analysis of Indian equities.

## What it does
- Pulls live NSE/BSE stock data using yfinance
- Computes daily returns, annualised volatility, rolling volatility, Sharpe ratio, and maximum drawdown
- Compares risk-adjusted performance across the Nifty 50 index and individual stocks

## Sample output — Risk Report (Jan 2023 – Dec 2024)

| Ticker | Annualised Vol | Sharpe Ratio | Max Drawdown | Max DD Date |
|--------|----------------|--------------|---------------|-------------|
| Nifty 50 (^NSEI) | 12.14% | 0.637 | -10.93% | 2024-11-21 |
| HDFC Bank | 19.82% | 0.065 | -19.91% | 2024-02-14 |
| Reliance | 20.36% | -0.154 | -24.46% | 2024-12-20 |

## Key finding
Individual stocks (HDFC Bank, Reliance) carried significantly more risk than the Nifty 50 index but did not proportionally reward investors — Reliance's negative Sharpe ratio over this period means investors would have been better off in risk-free government securities. This illustrates the practical value of diversification.
![Drawdown analysis](max_drawdown.png)

## Portfolio analysis 

Built an equal-weighted 3-stock portfolio (HDFC Bank, Reliance, Infosys) to test diversification in practice.

| Metric | Value |
|--------|-------|
| Portfolio annualised volatility | 14.91% |
| Simple average of individual stock volatilities | 21.09% |
| **Diversification benefit** | **6.18 percentage points lower** |
| Portfolio 1-day VaR (95%) | -1.33% |
| Portfolio 1-day VaR (99%) | -2.50% |

### Correlation matrix

| | HDFC Bank | Infosys | Reliance |
|---|---|---|---|
| HDFC Bank | 1.000 | 0.171 | 0.338 |
| Infosys | 0.171 | 1.000 | 0.246 |
| Reliance | 0.338 | 0.246 | 1.000 |

![Correlation heatmap](correlation_heatmap.png)

## Strategy comparison 

Built and compared three portfolio weighting strategies — Equal Weight, Defensive, and Decorrelation — over the same Jan 2023–Dec 2024 period, then evaluated them on a risk-adjusted basis rather than raw return alone.

| Strategy | Annualised Return | Annualised Vol | Sharpe Ratio | Max Drawdown |
|---|---|---|---|---|
| Equal Weight | 8.68% | 14.91% | 0.146 | -11.43% |
| Defensive | 8.21% | 15.01% | 0.114 | -11.84% |
| Decorrelation | 7.46% | 15.45% | 0.062 | -11.95% |

**Key finding:** Decorrelation had the highest cumulative return on the growth-of-₹1 chart, but the lowest Sharpe ratio — it took on more volatility and a deeper drawdown without enough extra return to compensate. Equal Weight, despite a lower headline return, had the best risk-adjusted performance. This reinforces the same lesson as Week 1: the strategy that "wins" on a chart isn't necessarily the best one once risk is accounted for.

**Key finding:** Combining three stocks from different sectors (banking, IT services, energy) reduced portfolio volatility by 6.18 percentage points versus the simple average of the individual stocks — a direct, quantified demonstration of diversification. This works because the pairwise correlations are low (0.17–0.34), meaning the stocks rarely have their worst days at the same time.

On a ₹10L portfolio, this analysis implies a 1-in-20 day loss exceeding ₹13,262 (95% VaR) and a 1-in-100 day loss exceeding ₹24,961 (99% VaR).

## Value at Risk — Historical vs. Monte Carlo 

Calculated 1-day Value at Risk (VaR) for each strategy using two methods: Historical VaR (based on actual realized daily returns) and Monte Carlo VaR (based on 10,000 simulated days drawn from a multivariate normal distribution fitted to the same data).

| Strategy | Historical VaR 95% | MC VaR 95% | Historical VaR 99% | MC VaR 99% |
|---|---|---|---|---|
| Equal Weight | -1.33% | -1.51% | -2.50% | -2.13% |
| Defensive | -1.37% | -1.49% | -2.77% | -2.13% |
| Decorrelation | -1.33% | -1.54% | -2.47% | -2.13% |

**Key finding:** The two methods disagree on which strategy is riskiest. Historical VaR flags Defensive as the worst performer at both confidence levels — despite being built to minimize variance, it has the worst tail risk historically. Monte Carlo VaR instead shows all three strategies converging to nearly identical 99% VaR (~-2.13%), understating the risk that Historical VaR captures. This is the classic limitation of a normal-distribution assumption: real markets have "fatter tails" than a bell curve predicts, so Monte Carlo simulation structurally cannot reproduce extreme historical events. This illustrates that **VaR methodology choice can change which portfolio looks riskiest** — a key reason risk teams use multiple approaches rather than relying on one.

Move from notebook-based analysis to an interactive Streamlit dashboard.

## Built with
Python, pandas, yfinance, numpy, scipy, Plotly

## Status
🚧 In progress — Week 3 of 8 complete. Next: Streamlit dashboard (Week 4).
