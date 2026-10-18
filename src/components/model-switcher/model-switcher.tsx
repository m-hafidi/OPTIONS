"use client";

import { useEffect, useRef, useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ThemeSwitch, type Theme } from "@/components/ui/theme-switch";
import ParameterCard, { isoDateInDays, type OptionParams } from "./parameter-card";
import ResultBand from "./result-band";
import { HistoryChart, SimulatedPaths } from "./charts";
import {
  fetchHistory,
  fetchPrice,
  fetchQuote,
  type History,
  type PriceResult,
  type Quote,
} from "@/lib/api";
import styles from "./model-switcher.module.css";

const MODELS = [
  {
    id: "black-scholes",
    label: "Black-Scholes",
    blurb:
      "Closed-form European price. Assumes constant rate and volatility, no dividends.",
  },
  {
    id: "monte-carlo",
    label: "Monte Carlo",
    blurb:
      "Simulates thousands of price paths and averages the discounted payoff.",
  },
  {
    id: "binomial",
    label: "Binomial Tree",
    blurb:
      "Builds a price tree over discrete steps and rolls the payoff back to today.",
  },
] as const;

type ModelId = (typeof MODELS)[number]["id"];

const initialParams: OptionParams = {
  ticker: "AAPL",
  strike: "",
  rate: 10,
  sigma: 20,
  expiry: isoDateInDays(365),
  sims: 10_000,
  paths: 100,
  steps: 1_500,
};

/** Stored choice, then the system preference, then light. Applies the theme before first paint so dark never flashes white. */
function readTheme(): Theme {
  const stored = window.localStorage.getItem("theme");
  if (stored === "dark" || stored === "light") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export default function ModelSwitcher() {
  const [model, setModel] = useState<ModelId>("black-scholes");
  // Parameters live here, not in the cards, so switching models keeps what you entered — the old app's session state.
  const [params, setParams] = useState<OptionParams>(initialParams);
  const [spot, setSpot] = useState<Quote | null>(null);
  const [quoteError, setQuoteError] = useState<string | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [pricing, setPricing] = useState(false);
  const [result, setResult] = useState<PriceResult | null>(null);
  const [priceError, setPriceError] = useState<string | null>(null);
  const [history, setHistory] = useState<History | null>(null);
  const [theme, setTheme] = useState<Theme>(() => {
    const initial = readTheme();
    document.documentElement.dataset.theme = initial;
    return initial;
  });

  useEffect(() => {
    window.localStorage.setItem("theme", theme);
  }, [theme]);

  // The switch reports the next theme; the page change itself runs as a view transition
  // from the whole-document snapshot — skipped for reduced motion, per the component's contract.
  const applyTheme = (next: Theme) => {
    const update = () => {
      document.documentElement.dataset.theme = next;
      setTheme(next);
    };
    const start = (
      document as Document & { startViewTransition?: (callback: () => void) => unknown }
    ).startViewTransition;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !start) update();
    else start.call(document, update);
  };

  // Every retire bumps this: a response only lands if it belongs to the request the
  // user is still looking at, so a slow price or history can't repaint retired figures.
  const generation = useRef(0);
  const inFlight = useRef<AbortController | null>(null);

  /** Retires the displayed figures and cancels whatever is still in flight. */
  const retire = () => {
    generation.current += 1;
    inFlight.current?.abort();
    inFlight.current = null;
    setPricing(false);
    setResult(null);
    setPriceError(null);
    setHistory(null);
  };

  // Unmount: invalidate and cancel, without touching state the component no longer owns.
  useEffect(
    () => () => {
      generation.current += 1;
      inFlight.current?.abort();
    },
    [],
  );

  const patch = (next: Partial<OptionParams>) => {
    setParams((current) => ({ ...current, ...next }));
    // A displayed price belongs to the parameters that produced it; changing anything retires it.
    retire();
  };

  // Live last close for the typed symbol, debounced like the old app's cached fetch.
  const lastTicker = useRef(params.ticker);
  useEffect(() => {
    if (params.ticker !== lastTicker.current) {
      lastTicker.current = params.ticker;
      // The seeded strike belongs to the previous symbol; clear it so the new quote re-seeds it.
      setParams((current) => (current.strike ? { ...current, strike: "" } : current));
    }
    const symbol = params.ticker.trim();
    if (!symbol) {
      setSpot(null);
      setQuoteError(null);
      setQuoteLoading(false);
      return;
    }
    setQuoteLoading(true);
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      fetchQuote(symbol, controller.signal)
        .then((quote) => {
          setSpot(quote);
          setQuoteError(null);
          // Seed the strike from the live price, the way the old app did — unless you already typed one.
          setParams((current) =>
            current.strike === ""
              ? { ...current, strike: quote.price.toFixed(2) }
              : current,
          );
        })
        .catch((error: unknown) => {
          if (error instanceof DOMException && error.name === "AbortError") return;
          setSpot(null);
          setQuoteError(
            error instanceof Error ? error.message : "Couldn't fetch a live price.",
          );
        })
        .finally(() => setQuoteLoading(false));
    }, 700);
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [params.ticker]);

  async function price() {
    const strike = Number(params.strike);
    if (!params.strike || !Number.isFinite(strike) || strike <= 0) {
      setPriceError("Enter a strike price to price the option.");
      return;
    }
    retire(); // clear yesterday's figures and cancel anything still out there
    const gen = generation.current;
    const controller = new AbortController();
    inFlight.current = controller;
    setPricing(true);
    try {
      const priced = await fetchPrice(
        {
          model,
          ticker: params.ticker,
          strike,
          rate: params.rate / 100,
          sigma: params.sigma / 100,
          expiry: params.expiry,
          sims: params.sims,
          steps: params.steps,
          paths: params.paths,
        },
        controller.signal,
      );
      if (gen !== generation.current) return;
      setResult(priced);
      // The old app drew the year-of-closes chart after pricing; a history hiccup shouldn't hide the prices.
      fetchHistory(params.ticker, controller.signal)
        .then((year) => {
          if (gen === generation.current) setHistory(year);
        })
        .catch(() => {
          if (gen === generation.current) setHistory(null);
        });
    } catch (error) {
      if (gen !== generation.current) return;
      setPriceError(
        error instanceof Error ? error.message : "Pricing failed unexpectedly.",
      );
    } finally {
      if (gen === generation.current) {
        inFlight.current = null;
        setPricing(false);
      }
    }
  }

  return (
    <Tabs
      value={model}
      // A figure priced by another model isn't this model's answer; switching retires it.
      onValueChange={(next) => {
        setModel(next as ModelId);
        retire();
      }}
      className="w-full max-w-[68rem]"
    >
      <div className={styles.toolbar}>
        <TabsList>
          {MODELS.map((entry) => (
            <TabsTrigger key={entry.id} value={entry.id}>
              {entry.label}
            </TabsTrigger>
          ))}
        </TabsList>
        <ThemeSwitch theme={theme} iconOnly onThemeChange={applyTheme} />
      </div>
      {MODELS.map((entry) => (
        <TabsContent key={entry.id} value={entry.id}>
          <p className={styles.blurb}>{entry.blurb}</p>
          <div className={styles.columns}>
            <div className={styles.controls}>
              <ParameterCard
                model={entry.id as ModelId}
                params={params}
                onChange={patch}
                spot={spot}
                quoteError={quoteError}
                quoteLoading={quoteLoading}
                pricing={pricing}
                onPrice={price}
              />
            </div>
            <div className={styles.results}>
              {priceError && (
                <p className={styles.priceError} role="alert">
                  {priceError}
                </p>
              )}
              {result ? (
                <>
                  <ResultBand result={result} />
                  <div
                    className={
                      model === "monte-carlo" && result.paths
                        ? `${styles.chartsRow} ${styles.split}`
                        : styles.chartsRow
                    }
                  >
                    {history && <HistoryChart history={history} />}
                    {model === "monte-carlo" && result.paths && (
                      <SimulatedPaths result={result} />
                    )}
                  </div>
                </>
              ) : (
                <p className={styles.placeholder} role="status">
                  Set your parameters, then price the option — the call and put
                  figures and the charts land here.
                </p>
              )}
            </div>
          </div>
        </TabsContent>
      ))}
    </Tabs>
  );
}
