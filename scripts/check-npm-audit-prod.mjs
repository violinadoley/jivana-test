#!/usr/bin/env node
/**
 * Fail CI if production npm audit reports high/critical advisories
 * outside an explicit allowlist (transitive deps with no fix yet).
 */
import { execSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const allowlistPath = join(root, ".github", "npm-audit-allowlist.json");
const frontendDir = join(root, "frontend");

const allowlist = JSON.parse(readFileSync(allowlistPath, "utf8"));
const allowedIds = new Set(allowlist.advisories ?? []);

let audit;
try {
  const out = execSync("npm audit --omit=dev --json", {
    cwd: frontendDir,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
  audit = JSON.parse(out);
} catch (err) {
  const stdout = err.stdout?.toString?.() ?? "";
  if (!stdout) {
    console.error(err.stderr?.toString?.() ?? err.message);
    process.exit(1);
  }
  audit = JSON.parse(stdout);
}

const vulnerabilities = audit.vulnerabilities ?? {};
const blocking = [];

for (const [name, info] of Object.entries(vulnerabilities)) {
  const severity = info.severity;
  if (severity !== "high" && severity !== "critical") {
    continue;
  }
  const via = info.via ?? [];
  const advisoryIds = via
    .filter((v) => typeof v === "object" && v.source)
    .map((v) => v.url?.split("/").pop())
    .filter(Boolean);

  const unlisted = advisoryIds.filter((id) => !allowedIds.has(id));
  if (unlisted.length > 0 || (advisoryIds.length === 0 && severity === "critical")) {
    blocking.push({ name, severity, unlisted, advisoryIds });
  }
}

if (blocking.length > 0) {
  console.error("Production npm audit: unallowlisted high/critical issues:\n");
  for (const b of blocking) {
    console.error(`- ${b.name} (${b.severity}): ${b.unlisted.join(", ") || "see npm audit"}`);
  }
  console.error("\nAllowlist: .github/npm-audit-allowlist.json (review by:", allowlist.review_by, ")");
  process.exit(1);
}

console.log(
  `Production npm audit OK (${allowedIds.size} allowlisted advisories documented).`
);
