# Option Pricing Models

Compare European option prices three ways — **Black–Scholes**, **Monte Carlo**, and a **binomial tree** — on live Yahoo Finance data, all on one screen.

**[▶ Try it live](https://m-hafidi.github.io/OPTIONS/)** — click to open the interactive preview.

![App preview](docs/preview.png)

Pick a method in the tabs, set the contract (ticker, strike, risk-free rate, volatility, exercise date — plus simulations and time steps where they apply), and hit **Price the option**. The call/put figures, the ticker's one-year price chart, and — on Monte Carlo — a grid of simulated paths appear *beside* the parameters, no scrolling. The live last close seeds the strike; switching symbols clears it and re-seeds from the new quote. Light and dark themes, scrubbable charts, keyboard access throughout.

> The live preview serves the full interface from GitHub Pages, but browsers can't call Yahoo Finance directly (CORS) and the pricing engines are Python — so on the preview, pricing shows the data-layer message instead of numbers. Run it locally (below) for real prices; nothing is ever faked.

## Quick start

Two processes: the pricing API and the web app.

### 1. Pricing API — Python

The API reuses the engines in `legacy/option_pricing/` untouched (their tests still apply).

```bash
python -m venv .venv
.venv/bin/pip install -r legacy/Requirements.txt -r server/requirements.txt
.venv/bin/pip install yfinance==1.7.0    # the legacy pin (0.2.31) no longer speaks Yahoo's API
npm run api                               # FastAPI on http://localhost:8000
```

On Windows use `.venv\Scripts\pip` instead of `.venv/bin/pip` (`npm run api` already handles its side).

### 2. Web app — Node

```bash
npm install
npm run dev        # Vite on http://localhost:5173
```

Open **http://localhost:5173** — the dev server proxies `/api` to the pricing API.

## API

| Endpoint | Returns |
| --- | --- |
| `GET /api/quote?ticker=AAPL` | Live last close and its date (cached 60s) |
| `GET /api/history?ticker=AAPL` | One year of daily closes, ~90 points, and the % change |
| `GET /api/price?model=black-scholes&ticker=AAPL&strike=343.46&rate=0.1&sigma=0.2&expiry=2027-10-18&sims=10000&steps=1500&paths=100` | Call and put prices from the selected engine; Monte Carlo also returns sampled paths for the chart |

`model` is one of `black-scholes`, `monte-carlo`, `binomial`; `rate` and `sigma` are decimals (0.1 = 10%).

## Project structure

```
src/                     React app (Vite · TypeScript · Tailwind CSS 4)
  components/ui/         tabs, theme switch, sparkline — uiarc registry components
  components/model-switcher/   the pricing desk: parameters, results, charts
  lib/api.ts             typed client for the pricing API
server/                  FastAPI service wrapping the legacy engines
legacy/                  the original Streamlit app (see legacy/README.md)
  option_pricing/        the pricing package: Black–Scholes, Monte Carlo, binomial
docs/preview.png         screenshot used above
```

## Notes

- The three models price the same contract differently on purpose — Monte Carlo within simulation error, the binomial tree within discretization error of the closed form. That comparison is the product.
- Live data comes from Yahoo Finance via `yfinance`; quotes are cached briefly, one-year history for five minutes.
- UI components are from the [uiarc](https://uiarc.dev) registry (tabs, sparkline, theme-switch), animated with [motion](https://motion.dev), built on Radix primitives.
