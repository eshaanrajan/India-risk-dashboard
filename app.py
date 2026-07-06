import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import minimize

# --- Page config (must be the first Streamlit command) ---
st.set_page_config(
    page_title="India Risk Dashboard",
    layout="wide"
)

st.title("India Risk Dashboard")
st.caption("5-stock NSE portfolio risk analytics — HDFC Bank, Reliance, Infosys, ICICI Bank, ITC")

# --- Ticker universe ---
TICKERS = {
    "HDFC Bank": "HDFCBANK.NS",
    "Reliance": "RELIANCE.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "ITC": "ITC.NS"
}

# --- Sector mapping ---
SECTOR_MAP = {
    "HDFC Bank": "Financials",
    "ICICI Bank": "Financials",
    "Reliance": "Energy",
    "Infosys": "IT",
    "ITC": "FMCG"
}

# --- Cached data loader ---
@st.cache_data
def load_data(tickers, start="2019-01-01"):
    data = yf.download(list(tickers.values()), start=start)["Close"]
    data.columns = list(tickers.keys())  # rename to friendly names
    return data

prices = load_data(TICKERS)

# --- Sidebar controls ---
st.sidebar.header("Portfolio Controls")

all_sectors = sorted(set(SECTOR_MAP.values()))

selected_sectors = st.sidebar.multiselect(
    "Select sectors",
    options=all_sectors,
    default=all_sectors
)

# Only show stocks that belong to the selected sector(s)
available_stocks = [stock for stock in TICKERS.keys() if SECTOR_MAP[stock] in selected_sectors]

selected_stocks = st.sidebar.multiselect(
    "Select stocks",
    options=available_stocks,
    default=available_stocks
)

# Guard: strip out any stale selections that are no longer valid under the current sector filter
selected_stocks = [stock for stock in selected_stocks if stock in available_stocks]

if not selected_stocks:
    st.warning("Please select at least one stock to view the dashboard.")
    st.stop()

strategy = st.sidebar.selectbox(
    "Weighting strategy",
    options=["Equal Weight", "Defensive (Min-Variance)", "Decorrelation"]
)

# --- Daily returns ---
returns = prices[selected_stocks].pct_change().dropna()

# --- Weight calculation functions ---
def equal_weight(stocks):
    n = len(stocks)
    return np.array([1/n] * n)

def defensive_weight(returns_df, max_weight=0.5):
    cov_matrix = returns_df.cov() * 10000  # scaled for optimizer stability
    n = len(returns_df.columns)

    def portfolio_variance(weights):
        return weights @ cov_matrix.values @ weights

    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = [(0, max_weight)] * n
    initial_guess = np.array([1/n] * n)

    result = minimize(
        portfolio_variance, initial_guess,
        method='SLSQP', bounds=bounds, constraints=constraints,
        options={'ftol': 1e-12}
    )
    return result.x

def decorrelation_weight(returns_df):
    corr_matrix = returns_df.corr()
    avg_corr = corr_matrix.mean(axis=1)
    inv_corr = 1 / avg_corr
    weights = inv_corr / inv_corr.sum()
    return weights.values

# --- Compute weights based on selected strategy ---
if strategy == "Equal Weight":
    weights = equal_weight(selected_stocks)
elif strategy == "Defensive (Min-Variance)":
    weights = defensive_weight(returns)
else:  # Decorrelation
    weights = decorrelation_weight(returns)

weights_df = pd.DataFrame({
    "Stock": selected_stocks,
    "Weight": weights,
    "Sector": [SECTOR_MAP[stock] for stock in selected_stocks]
})

# --- Generalized risk_report function ---
def risk_report(returns_series, weights_array=None, risk_free_rate=0.065):
    if weights_array is not None:
        portfolio_returns = returns_series @ weights_array
    else:
        portfolio_returns = returns_series

    annualized_return = portfolio_returns.mean() * 252
    annualized_vol = portfolio_returns.std() * np.sqrt(252)
    sharpe = (annualized_return - risk_free_rate) / annualized_vol

    cumulative = (1 + portfolio_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()

    return {
        "Annualized Return": annualized_return,
        "Annualized Volatility": annualized_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_drawdown
    }

metrics = risk_report(returns, weights)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Portfolio Weights")
    fig_weights = px.bar(weights_df, x="Stock", y="Weight", text_auto=".2%")
    fig_weights.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_weights, use_container_width=True)

with col2:
    st.subheader("Sector Allocation")
    sector_weights = weights_df.groupby("Sector")["Weight"].sum().reset_index()
    fig_sector = px.pie(sector_weights, names="Sector", values="Weight", hole=0.4)
    st.plotly_chart(fig_sector, use_container_width=True)

with col3:
    st.subheader("Correlation Heatmap")
    corr = returns.corr()
    fig_heatmap = px.imshow(
        corr, text_auto=".2f", zmin=-1, zmax=1,
        color_continuous_scale="RdBu_r"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.subheader(f"Risk Metrics — {strategy}")
metrics_df = pd.DataFrame({
    "Metric": ["Annualized Return", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown"],
    "Value": [
        f"{metrics['Annualized Return']:.2%}",
        f"{metrics['Annualized Volatility']:.2%}",
        f"{metrics['Sharpe Ratio']:.2f}",
        f"{metrics['Max Drawdown']:.2%}"
    ]
})
st.dataframe(metrics_df, hide_index=True, use_container_width=True)
# --- VaR calculations for selected strategy ---
def historical_var(portfolio_returns, confidence=0.95):
    return np.percentile(portfolio_returns, (1 - confidence) * 100)

def monte_carlo_var(portfolio_returns, confidence=0.95, n_simulations=5000):
    mu = portfolio_returns.mean()
    sigma = portfolio_returns.std()
    simulated_returns = np.random.normal(mu, sigma, n_simulations)
    return np.percentile(simulated_returns, (1 - confidence) * 100)

portfolio_returns = returns @ weights

hist_var = historical_var(portfolio_returns)
mc_var = monte_carlo_var(portfolio_returns)

st.subheader(f"Value at Risk (95% confidence) — {strategy}")

var_df = pd.DataFrame({
    "Method": ["Historical VaR", "Monte Carlo VaR"],
    "Daily VaR": [hist_var, mc_var]
})

fig_var = px.bar(
    var_df, x="Method", y="Daily VaR", text_auto=".2%",
    color="Method", color_discrete_sequence=["#EF553B", "#636EFA"]
)
fig_var.update_layout(yaxis_tickformat=".1%", showlegend=False)
st.plotly_chart(fig_var, use_container_width=True)

var_gap = abs(hist_var - mc_var)
if hist_var < mc_var:  # more negative = worse
    st.caption(
        f"Historical VaR ({hist_var:.2%}) is more severe than Monte Carlo VaR ({mc_var:.2%}) "
        f"by {var_gap:.2%} — consistent with fat tails: real returns have more extreme "
        f"days than a normal distribution assumes."
    )
else:
    st.caption(
        f"Monte Carlo VaR ({mc_var:.2%}) is more severe than Historical VaR ({hist_var:.2%}) "
        f"by {var_gap:.2%} for this selection."
    )
    # --- Cumulative Returns Chart ---
st.subheader(f"Cumulative Returns — {strategy}")

portfolio_cumulative = (1 + portfolio_returns).cumprod()

fig_cum = go.Figure()
fig_cum.add_trace(go.Scatter(
    x=portfolio_cumulative.index,
    y=portfolio_cumulative.values,
    mode="lines",
    name=strategy,
    line=dict(color="#00CC96", width=2)
))
fig_cum.update_layout(
    yaxis_title="Growth of ₹1 invested",
    xaxis_title="Date",
    hovermode="x unified"
)
st.plotly_chart(fig_cum, use_container_width=True)

# --- Stress Test Toggle ---
st.subheader("Stress Test")

run_stress_test = st.checkbox("Run COVID crash stress test (Feb–Apr 2020)")

if run_stress_test:
    stress_start = "2020-02-01"
    stress_end = "2020-04-30"

    stress_prices = prices.loc[stress_start:stress_end, selected_stocks]

    if stress_prices.empty:
        st.warning(
            "No price data available for the COVID stress window with the current "
            "stock selection. This can happen if a selected stock's data doesn't "
            "extend back to early 2020."
        )
    else:
        stress_returns = stress_prices.pct_change().dropna()
        stress_portfolio_returns = stress_returns @ weights
        stress_metrics = risk_report(stress_returns, weights)

        st.caption(f"Stress window: {stress_start} to {stress_end}")

        stress_metrics_df = pd.DataFrame({
            "Metric": ["Annualized Return", "Annualized Volatility", "Sharpe Ratio", "Max Drawdown"],
            "Normal Period": [
                f"{metrics['Annualized Return']:.2%}",
                f"{metrics['Annualized Volatility']:.2%}",
                f"{metrics['Sharpe Ratio']:.2f}",
                f"{metrics['Max Drawdown']:.2%}"
            ],
            "COVID Crash Period": [
                f"{stress_metrics['Annualized Return']:.2%}",
                f"{stress_metrics['Annualized Volatility']:.2%}",
                f"{stress_metrics['Sharpe Ratio']:.2f}",
                f"{stress_metrics['Max Drawdown']:.2%}"
            ]
        })
        st.dataframe(stress_metrics_df, hide_index=True, use_container_width=True)

        stress_cumulative = (1 + stress_portfolio_returns).cumprod()
        fig_stress = go.Figure()
        fig_stress.add_trace(go.Scatter(
            x=stress_cumulative.index,
            y=stress_cumulative.values,
            mode="lines",
            name="COVID Crash Performance",
            line=dict(color="#EF553B", width=2)
        ))
        fig_stress.update_layout(
            yaxis_title="Growth of ₹1 invested",
            xaxis_title="Date",
            hovermode="x unified"
        )
        st.plotly_chart(fig_stress, use_container_width=True)
