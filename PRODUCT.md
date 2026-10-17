# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Retail investors, traders, and finance students who want a fast European option price on a live ticker, and want to see how the three classical models differ. Single-user tool; no accounts, roles, or collaboration. *(Inferred from the repository and brief; no user research exists.)*

## Product Purpose

Price European call and put options from live Yahoo Finance data using three models — Black-Scholes, Monte Carlo, Binomial tree — and make the effect of each parameter (strike, rate, volatility, maturity) tangible. Success: a user picks a model, adjusts parameters, and reads a defensible call/put price within seconds.

## Positioning

Three textbook pricing models side by side on one live-data tool, each exposing its own mechanism (closed form, simulated paths, price tree) instead of a single black-box number.

## Operating Context

Runs locally as a Streamlit app (`.venv` + `streamlit run streamlit_app.py`); Docker and GCP deploy paths documented in README. All market data is fetched live from the Yahoo Finance API via `yfinance` (upgraded to 1.7.0 — the pinned 0.2.31 no longer works against Yahoo's API). Users iterate: change a parameter, rerun, compare.

## Capabilities and Constraints

- Models: Black-Scholes (closed form), Monte Carlo (user-set simulation count), Binomial CRR (user-set time steps). European options only; no dividends; constant risk-free rate and volatility.
- Inputs: ticker symbol, strike price, risk-free rate (%), volatility sigma (%), exercise date; plus model-specific simulation/step counts.
- Spot price is always the last close from one year of Yahoo history; the strike range is suggested from the live price.
- Output: call and put price, a historical price chart, and (Monte Carlo) simulated-path chart. The raw data table was deliberately removed in the redesign.
- Python 3.12, Streamlit 1.29, pinned deps in `Requirements.txt`.
- Undecided / not built: American options, dividends, Greeks — not requested.

## Brand Commitments

Visual direction pinned by the user and binding: an **Airbnb-like aesthetic — bold, simple, minimalist — with dark mode as the default plus a light-mode toggle**. No logo, brand name, or other brand assets exist.

## Evidence on Hand

`README.md` (method descriptions, run instructions), `media/*.gif` demos of the previous UI, `option_pricing_test.py` exercising all three models, live Yahoo Finance data. No metrics, testimonials, or customer proof exist; none may be invented.

## Product Principles

1. Price first — the number the user came for is the loudest thing on screen.
2. One decision per screen — pick a model, set parameters, read the result.
3. Show the mechanism — every model keeps its visual proof (price history, simulated paths).
4. Live data only — never hardcode a price; if data can't be fetched, say so plainly.
5. Honest limits — European options, constant rate and volatility; assumptions stated where they matter.

## Accessibility & Inclusion

Every control keeps its native Streamlit label and semantics; text and control contrast must hold in both dark and light themes; results must be readable without relying on color alone.
