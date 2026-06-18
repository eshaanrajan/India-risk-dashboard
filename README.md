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

## Built with
Python, pandas, yfinance, matplotlib, numpy

## Status
🚧 In progress — Week 1 of 8. Currently building portfolio-level analysis (Week 2-3).
