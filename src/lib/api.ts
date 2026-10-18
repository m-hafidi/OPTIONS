/** Client for the FastAPI pricing service (proxied by Vite at /api). */

export interface Quote {
  ticker: string;
  price: number;
  asOf: string;
}

export interface PriceResult {
  model: string;
  ticker: string;
  spot: number;
  strike: number;
  days: number;
  call: number;
  put: number;
  /** Monte Carlo only: sampled simulated paths, evenly drawn from the run. */
  paths?: number[][];
  /** One label per point across every path, such as "Day 30". */
  pathLabels?: string[];
  /** How many simulations the run actually used. */
  pathsTotal?: number;
}

/** One year of daily closes, downsampled for the trend chart. */
export interface History {
  ticker: string;
  closes: number[];
  labels: string[];
  /** First close to last close, in percent. */
  changePct: number;
}

export interface PriceRequest {
  model: "black-scholes" | "monte-carlo" | "binomial";
  ticker: string;
  strike: number;
  /** Decimal, e.g. 0.1 for 10%. */
  rate: number;
  /** Decimal, e.g. 0.2 for 20%. */
  sigma: number;
  expiry: string;
  sims: number;
  steps: number;
  /** Monte Carlo only: how many paths to plot (the old app's "Paths to plot"). */
  paths: number;
}

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;
    throw new Error(body?.detail ?? `Request failed (${response.status}).`);
  }
  return (await response.json()) as T;
}

export function fetchQuote(ticker: string, signal?: AbortSignal): Promise<Quote> {
  return get<Quote>(`/api/quote?ticker=${encodeURIComponent(ticker)}`, signal);
}

export function fetchHistory(ticker: string, signal?: AbortSignal): Promise<History> {
  return get<History>(`/api/history?ticker=${encodeURIComponent(ticker)}`, signal);
}

export function fetchPrice(request: PriceRequest, signal?: AbortSignal): Promise<PriceResult> {
  const query = new URLSearchParams({
    model: request.model,
    ticker: request.ticker,
    strike: String(request.strike),
    rate: String(request.rate),
    sigma: String(request.sigma),
    expiry: request.expiry,
    sims: String(request.sims),
    steps: String(request.steps),
    paths: String(request.paths),
  });
  return get<PriceResult>(`/api/price?${query.toString()}`, signal);
}
