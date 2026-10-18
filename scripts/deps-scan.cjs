// Reports every external package imported by files under src/ (dev aid).
const fs = require("fs"), path = require("path");
const pkgs = new Set();
function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p);
    else if (/\.(ts|tsx)$/.test(e.name)) {
      const c = fs.readFileSync(p, "utf8");
      for (const m of c.matchAll(/from\s+["']([^"']+)["']/g)) {
        const spec = m[1];
        if (spec.startsWith(".") || spec.startsWith("/")) continue;
        const parts = spec.split("/");
        pkgs.add(spec.startsWith("@") ? parts.slice(0, 2).join("/") : parts[0]);
      }
    }
  }
}
walk("src");
console.log([...pkgs].sort().join("\n"));
