"""Live-quote and pricing API for the React front end.

Reuses the pricing engines from legacy/option_pricing — the same Black-Scholes,
Monte Carlo, and binomial implementations the original Streamlit app used — so
the math stays in one place. Run with:

    .venv/Scripts/python -m uvicorn main:app --port 8000   (from the repo root)
"""
import sys
from datetime import date
from pathlib import Path
from time import monotonic

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

sys.path.append(str(Path(__file__).resolve().parent.parent / "legacy"))
from option_pricing import BlackScholesModel, BinomialTreeModel, MonteCarloPricing  # noqa: E402

app = FastAPI(title="Option pricing API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quotes are cached briefly so typing a symbol or re-pricing doesn't hammer Yahoo.
_QUOTE_TTL_SECONDS = 60.0
_quote_cache: dict[str, tuple[float, dict]] = {}

# One-year history changes once a day; cache it longer.
_HISTORY_TTL_SECONDS = 300.0
_history_cache: dict[str, tuple[float, dict]] = {}


def last_close(symbol: str) -> dict:
    """Last close for a symbol, cached for a minute. Mirrors the old app's get_current_price."""
    now = monotonic()
    cached = _quote_cache.get(symbol)
    if cached and now - cached[0] < _QUOTE_TTL_SECONDS:
        return cached[1]

    try:
        history = yf.Ticker(symbol).history(period="1d")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Couldn't fetch a live price for “{symbol}”: {exc}")
    if history.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Couldn't fetch a live price for “{symbol}”. Check the symbol and your connection.",
        )
    quote = {
        "ticker": symbol,
        "price": round(float(history["Close"].iloc[-1]), 4),
        "asOf": str(history.index[-1].date()),
    }
    _quote_cache[symbol] = (now, quote)
    return quote


@app.get("/api/quote")
def quote(ticker: str = Query(..., min_length=1, max_length=12)):
    return last_close(ticker.strip().upper())


@app.get("/api/history")
def history(ticker: str = Query(..., min_length=1, max_length=12)):
    """One year of daily closes, downsampled to ~90 points for the trend chart."""
    symbol = ticker.strip().upper()
    now = monotonic()
    cached = _history_cache.get(symbol)
    if cached and now - cached[0] < _HISTORY_TTL_SECONDS:
        return cached[1]

    try:
        data = yf.Ticker(symbol).history(period="1y")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Couldn't fetch price history for “{symbol}”: {exc}")
    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Couldn't fetch price history for “{symbol}”. Check the symbol and your connection.",
        )
    closes_all = [round(float(value), 4) for value in data["Close"].tolist()]
    labels_all = [index.strftime("%b %d") for index in data.index]
    step = max(1, len(closes_all) // 90)
    closes = closes_all[::step]
    labels = labels_all[::step]
    if closes[-1] != closes_all[-1]:
        closes.append(closes_all[-1])
        labels.append(labels_all[-1])
    change = (closes_all[-1] / closes_all[0] - 1) * 100 if closes_all[0] else 0.0
    payload = {
        "ticker": symbol,
        "closes": closes,
        "labels": labels,
        "changePct": round(change, 2),
    }
    _history_cache[symbol] = (now, payload)
    return payload


@app.get("/api/price")
def price(
    model: str,
    ticker: str = Query(..., min_length=1, max_length=12),
    strike: float = Query(..., gt=0),
    rate: float = Query(..., ge=0, le=1),
    sigma: float = Query(..., gt=0, le=5),
    expiry: date = Query(...),
    sims: int = Query(10_000, ge=100, le=100_000),
    steps: int = Query(1_500, ge=100, le=20_000),
    paths: int = Query(100, ge=0, le=200),
):
    """Price a European option. `rate` and `sigma` are decimals (0.1 = 10%)."""
    if model not in ("black-scholes", "monte-carlo", "binomial"):
        raise HTTPException(status_code=400, detail=f"Unknown model “{model}”.")
    days = (expiry - date.today()).days
    if days < 1:
        raise HTTPException(status_code=400, detail="The exercise date must be in the future.")

    spot = last_close(ticker.strip().upper())["price"]

    try:
        if model == "black-scholes":
            engine = BlackScholesModel(spot, strike, days, rate, sigma)
        elif model == "monte-carlo":
            engine = MonteCarloPricing(spot, strike, days, rate, sigma, sims)
            engine.simulate_prices()
        else:
            engine = BinomialTreeModel(spot, strike, days, rate, sigma, steps)
        call = float(engine.calculate_option_price("Call Option"))
        put = float(engine.calculate_option_price("Put Option"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pricing failed: {exc}")

    result = {
        "model": model,
        "ticker": ticker.strip().upper(),
        "spot": spot,
        "strike": strike,
        "days": days,
        "call": call,
        "put": put,
    }

    # Monte Carlo also returns a drawable sample of the simulated paths: at most 12
    # paths (the sparkline grid is the compact UI, not the old 200-line matplotlib wall),
    # each downsampled to ~60 points. The user's "Paths to plot" still trims the pool.
    if model == "monte-carlo":
        matrix = engine.simulation_results_S
        column_count = int(matrix.shape[1])
        shown = max(1, min(paths or 100, 12, column_count))
        columns = (
            [round(index * (column_count - 1) / (shown - 1)) for index in range(shown)]
            if shown > 1
            else [0]
        )
        row_step = max(1, days // 60)
        rows = list(range(0, days, row_step))
        if rows[-1] != days - 1:
            rows.append(days - 1)
        result["paths"] = [
            [round(float(matrix[row, column]), 4) for row in rows] for column in columns
        ]
        result["pathLabels"] = [f"Day {row}" for row in rows]
        result["pathsTotal"] = column_count

    return result
