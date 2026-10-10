import { expect, test } from "@playwright/test";

/**
 * Smoke against deployed Firebase Hosting + live Cloud Run API
 * (NEXT_PUBLIC_API_URL baked into the static export at build time).
 */
test.describe("Deployed hosting smoke", () => {
  test("home and dashboard load", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    await page.goto("/dashboard");
    const mvp = page.getByRole("heading", { name: /discharge medication reconciliation/i });
    const legacy = page.getByRole("heading", { name: /healthcare enterprise workspace/i });
    await expect(mvp.or(legacy)).toBeVisible();
  });

  test("SMART launch page loads", async ({ page }) => {
    await page.goto("/smart/launch");
    await expect(page.getByRole("heading", { name: /SMART on FHIR launch/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Open JIVANA workspace/i })).toBeVisible();
  });
});
