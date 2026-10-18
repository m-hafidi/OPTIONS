#!/usr/bin/env node
/**
 * One-shot helper: downloads uiarc registry items (shadcn registry format)
 * and materialises their files into src/, following registryDependencies.
 *
 * Usage: node scripts/fetch-registry.mjs <registry-url> [...more]
 */
import { mkdirSync, writeFileSync, existsSync, readFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";

const ROOT = process.cwd();
const seen = new Set();
const npmDeps = new Set();
const queued = process.argv.slice(2);

async function fetchItem(url) {
  if (seen.has(url)) return;
  seen.add(url);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  const item = await res.json();
  console.log(`item: ${item.name} (${item.type})`);
  for (const d of item.dependencies ?? []) npmDeps.add(d);

  for (const f of item.files ?? []) {
    // Keep registry paths verbatim under src/ so `@/registry/...` and
    // `@/lib/...` imports (the Arc convention) resolve via @/ -> src/.
    const abs = join(ROOT, "src", f.path);
    if (!existsSync(abs)) {
      mkdirSync(dirname(abs), { recursive: true });
      writeFileSync(abs, f.content ?? "", "utf8");
      console.log(`  + src/${f.path}`);
    } else {
      console.log(`  = src/${f.path} (kept existing)`);
    }
  }

  for (const dep of item.registryDependencies ?? []) {
    const depUrl = dep.startsWith("http") ? dep : `https://uiarc.dev/r/${dep}.json`;
    await fetchItem(depUrl);
  }
}

for (const url of queued) await fetchItem(url);
console.log(`done: ${seen.size} registry items`);
console.log(`npm deps: ${[...npmDeps].sort().join(", ") || "(none declared)"}`);
