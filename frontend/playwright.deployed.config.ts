import { defineConfig, devices } from "@playwright/test";

/** Run against Firebase Hosting (no local webServer). */
const baseURL =
  process.env.PLAYWRIGHT_BASE_URL ?? "https://project-bf77a013-c0b3-413c-a75.web.app";

export default defineConfig({
  testDir: "./e2e",
  testMatch: "deployed-smoke.spec.ts",
  fullyParallel: false,
  retries: 1,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
