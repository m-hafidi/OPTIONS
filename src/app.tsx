import ModelSwitcher from "@/components/model-switcher/model-switcher";

export default function App() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        // Centers when there's room; falls back to the top when a short window makes the content taller.
        alignContent: "safe center",
        justifyItems: "center",
        padding: "var(--space-6)",
        background: "var(--background)",
        color: "var(--foreground)",
      }}
    >
      <ModelSwitcher />
    </main>
  );
}
