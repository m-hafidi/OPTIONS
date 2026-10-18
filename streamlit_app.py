import streamlit as st
from enum import Enum
from datetime import datetime, timedelta
import yfinance as yf

from option_pricing import BlackScholesModel, MonteCarloPricing, BinomialTreeModel, Ticker
import app_theme


class Model(Enum):
    BLACK_SCHOLES = "Black–Scholes"
    MONTE_CARLO = "Monte Carlo"
    BINOMIAL = "Binomial tree"


# ---------------------------------------------------------------- fetching --
@st.cache_data
def get_historical_data(ticker):
    return Ticker.get_historical_data(ticker)


@st.cache_data
def get_current_price(ticker):
    data = yf.Ticker(ticker).history(period="1d")
    return data["Close"].iloc[-1]


# ------------------------------------------------------------------ pieces --
def theme_colors():
    p = app_theme.DARK if app_theme.current() == "dark" else app_theme.LIGHT
    return p


def topbar():
    left, right = st.columns([3, 2])
    with left:
        st.markdown("<h1>Option pricing</h1>", unsafe_allow_html=True)
    with right:
        with st.container():
            st.radio("Theme", ["Dark", "Light"], horizontal=True, label_visibility="collapsed",
                     key="theme_radio",
                     on_change=lambda: st.session_state.update(
                         theme="dark" if st.session_state.theme_radio == "Dark" else "light"))


def param_inputs(model):
    """Shared parameter card. Returns a dict of inputs, or None if the ticker
    price could not be fetched (a friendly error is already shown)."""
    ticker = st.text_input("Ticker symbol", value="AAPL",
                           placeholder="e.g. AAPL").strip().upper()

    try:
        price = get_current_price(ticker)
    except Exception:
        price = None

    if price is None:
        st.error(f"Couldn't fetch a live price for “{ticker}”. Check the symbol and your connection.")
        return None

    st.caption(f"Last close · ${price:,.2f}")

    min_strike = max(0.1, round(price * 0.5, 2))
    max_strike = round(price * 2, 2)
    strike = st.number_input(
        "Strike price", min_value=min_strike, max_value=max_strike,
        value=round(float(price), 2), step=0.01, format="%.2f",
    )

    c1, c2 = st.columns(2)
    with c1:
        rate = st.slider("Risk-free rate", 0, 100, 10, format="%d%%") / 100
    with c2:
        sigma = st.slider("Volatility (σ)", 0, 100, 20, format="%d%%") / 100

    exercise = st.date_input(
        "Exercise date",
        min_value=datetime.today() + timedelta(days=1),
        value=datetime.today() + timedelta(days=365),
    )
    days = (exercise - datetime.now().date()).days

    extra = {}
    if model == Model.MONTE_CARLO:
        extra["sims"] = st.slider("Simulations", 100, 100_000, 10_000, step=100)
        extra["paths"] = st.slider("Paths to plot", 0, max(1, extra["sims"] // 10), 100)
    elif model == Model.BINOMIAL:
        extra["steps"] = st.slider("Time steps", 100, 20_000, 1_500, step=100)

    return {
        "ticker": ticker, "spot": float(price), "strike": float(strike),
        "rate": rate, "sigma": sigma, "days": days, **extra,
    }


def price(model, p):
    """Dispatch to the selected model. Returns (call, put)."""
    spot, strike, days, rate, sigma = p["spot"], p["strike"], p["days"], p["rate"], p["sigma"]
    if model == Model.BLACK_SCHOLES:
        m = BlackScholesModel(spot, strike, days, rate, sigma)
    elif model == Model.MONTE_CARLO:
        m = MonteCarloPricing(spot, strike, days, rate, sigma, p["sims"])
        m.simulate_prices()
    else:
        m = BinomialTreeModel(spot, strike, days, rate, sigma, p["steps"])
    return m.calculate_option_price("Call Option"), m.calculate_option_price("Put Option"), m


def result_band(call, put, ticker):
    st.markdown(
        f"""
        <div class="result-grid">
          <div class="result-cell accent">
            <div class="result-kind">Call · {ticker}</div>
            <div class="result-figure">${call:,.2f}</div>
            <div class="result-note">Right to buy at the strike</div>
          </div>
          <div class="result-cell">
            <div class="result-kind">Put · {ticker}</div>
            <div class="result-figure">${put:,.2f}</div>
            <div class="result-note">Right to sell at the strike</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def draw_charts(data, params, mc, colors):
    fig = Ticker.plot_data(data, params["ticker"], "Close",
                           text_color=colors["text"], grid_color=colors["border"],
                           line_color=colors["accent"])
    st.pyplot(fig)
    if mc is not None:
        fig2 = mc.plot_simulation_results(
            min(params.get("paths", 0), 200),
            text_color=colors["text"], grid_color=colors["border"],
            path_color=colors["accent"], strike_color=colors["text2"])
        st.pyplot(fig2)


# -------------------------------------------------------------------- main --
def main():
    st.set_page_config(page_title="Option pricing", page_icon=None, layout="centered")
    app_theme.inject()
    topbar()

    model_label = st.radio(
        "Model", [m.value for m in Model], horizontal=True,
        label_visibility="collapsed", key="model_radio",
    )
    model = Model(model_label)

    blurb = {
        Model.BLACK_SCHOLES: "Closed-form European price. Assumes constant rate and volatility, no dividends.",
        Model.MONTE_CARLO: "Simulates thousands of price paths and averages the discounted payoff.",
        Model.BINOMIAL: "Builds a price tree over discrete steps and rolls the payoff back to today.",
    }[model]
    st.caption(blurb)

    st.markdown("")
    with st.container(border=True):
        st.markdown("#### Contract parameters")
        params = param_inputs(model)

    if params is None:
        return

    st.markdown("")
    clicked = st.button(f"Price the option", type="primary")

    if not clicked:
        st.info("Set your parameters, then price the option.")
        return

    with st.spinner("Fetching data and pricing…"):
        try:
            data = get_historical_data(params["ticker"])
        except Exception as e:
            st.error(f"Couldn't fetch history for “{params['ticker']}”: {e}")
            return
        call, put, mc = price(model, params)

    st.markdown("")
    result_band(call, put, params["ticker"])
    st.markdown("")
    draw_charts(data, params, mc if model == Model.MONTE_CARLO else None, theme_colors())


if __name__ == "__main__":
    main()
