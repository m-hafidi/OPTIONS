import type { PriceResult } from "@/lib/api";
import styles from "./result-band.module.css";

const money = (value: number) =>
  value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

/** The call/put figures from the old app's result band: price first, biggest thing on screen. */
export default function ResultBand({ result }: { result: PriceResult }) {
  return (
    <section className={styles.band} aria-label="Option prices">
      <div className={styles.cell}>
        <span className={styles.kind}>Call · {result.ticker}</span>
        <span className={`${styles.figure} ${styles.accent}`}>{money(result.call)}</span>
        <span className={styles.note}>Right to buy at the strike</span>
      </div>
      <div className={styles.cell}>
        <span className={styles.kind}>Put · {result.ticker}</span>
        <span className={styles.figure}>{money(result.put)}</span>
        <span className={styles.note}>Right to sell at the strike</span>
      </div>
    </section>
  );
}
