import { Sparkline } from "@/components/ui/sparkline";
import type { History, PriceResult } from "@/lib/api";
import styles from "./charts.module.css";

const money = (value: number) =>
  value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

const signedPct = (value: number) =>
  `${value >= 0 ? "+" : "−"}${Math.abs(value).toFixed(1)}%`;

/** The old app's year-of-closes chart, drawn as one scrubbable sparkline. */
export function HistoryChart({ history }: { history: History }) {
  const latest = history.closes[history.closes.length - 1] ?? 0;
  return (
    <section className={styles.section} aria-label="Price history">
      <h3 className={styles.heading}>Last 12 months</h3>
      <Sparkline
        data={history.closes}
        labels={history.labels}
        label={`${history.ticker} · close`}
        value={money(latest)}
        change={`${signedPct(history.changePct)} over 1y`}
        formatValue={money}
        width={280}
        height={56}
      />
    </section>
  );
}

/** The old app's simulated-paths chart: one sparkline per sampled path, tinted by where it finishes against the strike. */
export function SimulatedPaths({ result }: { result: PriceResult }) {
  const paths = result.paths ?? [];
  const labels = result.pathLabels ?? [];
  return (
    <section className={styles.section} aria-label="Simulated price paths">
      <h3 className={styles.heading}>Simulated paths</h3>
      <p className={styles.note}>
        {paths.length.toLocaleString("en-US")} of{" "}
        {(result.pathsTotal ?? 0).toLocaleString("en-US")} simulations, sampled
        evenly. Each line ends at its expiry price — green finishes above the{" "}
        {money(result.strike)} strike (in the money for a call), red below.
      </p>
      <div className={styles.grid}>
        {paths.map((path, index) => {
          const start = path[0] ?? 1;
          const end = path[path.length - 1] ?? 0;
          return (
            <Sparkline
              key={index}
              data={path}
              labels={labels}
              label={`Path ${index + 1}`}
              value={money(end)}
              change={signedPct((end / start - 1) * 100)}
              tone={end > result.strike ? "success" : "danger"}
              formatValue={money}
              width={150}
              height={44}
              interactive={false}
            />
          );
        })}
      </div>
    </section>
  );
}
