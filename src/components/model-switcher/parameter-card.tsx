"use client";

import { useId } from "react";
import type { Quote } from "@/lib/api";
import styles from "./parameter-card.module.css";

type ModelId = "black-scholes" | "monte-carlo" | "binomial";

/** Every field of the contract-parameter card. Owned by the model switcher so values survive switching tabs. */
export interface OptionParams {
  ticker: string;
  strike: string;
  rate: number;
  sigma: number;
  expiry: string;
  sims: number;
  paths: number;
  steps: number;
}

/** yyyy-mm-dd for date inputs, `days` from today. */
export function isoDateInDays(days: number) {
  const date = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
  return date.toISOString().slice(0, 10);
}

const money = (value: number) =>
  value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

interface ParameterCardProps {
  model: ModelId;
  params: OptionParams;
  onChange: (patch: Partial<OptionParams>) => void;
  spot: Quote | null;
  quoteError: string | null;
  quoteLoading: boolean;
  pricing: boolean;
  onPrice: () => void;
}

/** The shared contract-parameter card from the old Streamlit app, with the model-specific knob per tab. */
export default function ParameterCard({
  model,
  params,
  onChange,
  spot,
  quoteError,
  quoteLoading,
  pricing,
  onPrice,
}: ParameterCardProps) {
  const id = useId();
  const field = (name: string) => `${id}-${name}`;
  // With a live price in hand, the strike snaps to the old app's suggested band: 50%–200% of spot.
  const strikeBounds = spot
    ? {
        min: Math.max(0.1, Number((spot.price * 0.5).toFixed(2))),
        max: Number((spot.price * 2).toFixed(2)),
      }
    : null;

  return (
    <form
      className={styles.card}
      onSubmit={(event) => {
        event.preventDefault();
        onPrice();
      }}
    >
      <h2 className={styles.title}>Contract parameters</h2>

      <div className={styles.field}>
        <label className={styles.label} htmlFor={field("ticker")}>
          Ticker symbol
        </label>
        <input
          id={field("ticker")}
          className={styles.input}
          value={params.ticker}
          onChange={(event) => onChange({ ticker: event.target.value.toUpperCase() })}
          placeholder="e.g. AAPL"
          autoComplete="off"
          spellCheck={false}
        />
        {quoteError ? (
          <p className={`${styles.hint} ${styles.error}`} role="alert">
            {quoteError}
          </p>
        ) : spot ? (
          <p className={styles.hint}>
            Last close · {money(spot.price)} ({spot.asOf})
          </p>
        ) : (
          <p className={styles.hint}>
            {quoteLoading
              ? "Fetching the last close…"
              : "The live last close appears here once the data layer is connected."}
          </p>
        )}
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor={field("strike")}>
          Strike price
        </label>
        <input
          id={field("strike")}
          className={styles.input}
          type="number"
          min={strikeBounds?.min ?? 0.01}
          max={strikeBounds?.max}
          step="0.01"
          inputMode="decimal"
          placeholder="e.g. 189.95"
          value={params.strike}
          onChange={(event) => onChange({ strike: event.target.value })}
        />
      </div>

      <div className={styles.row}>
        <div className={styles.field}>
          <div className={styles.labelRow}>
            <label className={styles.label} htmlFor={field("rate")}>
              Risk-free rate
            </label>
            <output className={styles.value} htmlFor={field("rate")}>
              {params.rate}%
            </output>
          </div>
          <input
            id={field("rate")}
            className={styles.slider}
            type="range"
            min={0}
            max={100}
            step={1}
            value={params.rate}
            onChange={(event) => onChange({ rate: Number(event.target.value) })}
          />
        </div>
        <div className={styles.field}>
          <div className={styles.labelRow}>
            <label className={styles.label} htmlFor={field("sigma")}>
              Volatility (σ)
            </label>
            <output className={styles.value} htmlFor={field("sigma")}>
              {params.sigma}%
            </output>
          </div>
          <input
            id={field("sigma")}
            className={styles.slider}
            type="range"
            min={0}
            max={100}
            step={1}
            value={params.sigma}
            onChange={(event) => onChange({ sigma: Number(event.target.value) })}
          />
        </div>
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor={field("expiry")}>
          Exercise date
        </label>
        <input
          id={field("expiry")}
          className={styles.input}
          type="date"
          min={isoDateInDays(1)}
          value={params.expiry}
          onChange={(event) => onChange({ expiry: event.target.value })}
        />
      </div>

      {model === "monte-carlo" && (
        <>
          <div className={styles.field}>
            <div className={styles.labelRow}>
              <label className={styles.label} htmlFor={field("sims")}>
                Simulations
              </label>
              <output className={styles.value} htmlFor={field("sims")}>
                {params.sims.toLocaleString("en-US")}
              </output>
            </div>
            <input
              id={field("sims")}
              className={styles.slider}
              type="range"
              min={100}
              max={100_000}
              step={100}
              value={params.sims}
              onChange={(event) => {
                const next = Number(event.target.value);
                onChange({
                  sims: next,
                  paths: Math.min(params.paths, Math.max(1, Math.floor(next / 10))),
                });
              }}
            />
          </div>
          <div className={styles.field}>
            <div className={styles.labelRow}>
              <label className={styles.label} htmlFor={field("paths")}>
                Paths to plot
              </label>
              <output className={styles.value} htmlFor={field("paths")}>
                {params.paths}
              </output>
            </div>
            <input
              id={field("paths")}
              className={styles.slider}
              type="range"
              min={0}
              max={Math.max(1, Math.floor(params.sims / 10))}
              step={1}
              value={params.paths}
              onChange={(event) => onChange({ paths: Number(event.target.value) })}
            />
          </div>
        </>
      )}

      {model === "binomial" && (
        <div className={styles.field}>
          <div className={styles.labelRow}>
            <label className={styles.label} htmlFor={field("steps")}>
              Time steps
            </label>
            <output className={styles.value} htmlFor={field("steps")}>
              {params.steps.toLocaleString("en-US")}
            </output>
          </div>
          <input
            id={field("steps")}
            className={styles.slider}
            type="range"
            min={100}
            max={20_000}
            step={100}
            value={params.steps}
            onChange={(event) => onChange({ steps: Number(event.target.value) })}
          />
        </div>
      )}

      <button className={styles.submit} type="submit" disabled={pricing}>
        {pricing ? "Pricing…" : "Price the option"}
      </button>
    </form>
  );
}
