import { expect, test } from "@playwright/test";

test.describe("Critical paths", () => {
  test("landing page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("SMART launch page loads", async ({ page }) => {
    await page.goto("/smart/launch?iss=https%3A%2F%2Fexample.fhir&launch=demo");
    await expect(page.getByRole("heading", { name: /SMART on FHIR launch/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Open JIVANA workspace/i })).toBeVisible();
  });

  test("dashboard route loads", async ({ page }) => {
    await page.goto("/dashboard");
    const mvp = page.getByRole("heading", {
      name: /discharge medication reconciliation/i,
    });
    const legacy = page.getByRole("heading", {
      name: /healthcare enterprise workspace/i,
    });
    await expect(mvp.or(legacy)).toBeVisible();
  });

  test("workbench shows create case control when MVP enabled", async ({ page }) => {
    await page.goto("/dashboard");
    const createBtn = page.getByRole("button", { name: /start new discharge review/i });
    const legacyHeading = page.getByRole("heading", {
      name: /healthcare enterprise workspace/i,
    });
    if (await legacyHeading.isVisible()) {
      test.skip();
    }
    await expect(createBtn).toBeVisible();
  });

  test("hybrid workspace exposes meeting tools tab when MVP enabled", async ({ page }) => {
    await page.goto("/dashboard");
    const legacyHeading = page.getByRole("heading", {
      name: /healthcare enterprise workspace/i,
    });
    if (await legacyHeading.isVisible()) {
      test.skip();
    }
    const meetingsTab = page.getByRole("button", { name: /^meetings$/i });
    await expect(meetingsTab).toBeVisible();
    await meetingsTab.click();
    await expect(page.getByRole("heading", { name: /meeting & handoff briefs/i })).toBeVisible();
  });

  test("hybrid workspace tab journey when MVP enabled", async ({ page }) => {
    await page.goto("/dashboard");
    const legacyHeading = page.getByRole("heading", {
      name: /healthcare enterprise workspace/i,
    });
    if (await legacyHeading.isVisible()) {
      test.skip();
    }

    const tabs: { label: RegExp; heading: RegExp }[] = [
      { label: /^search$/i, heading: /policy & knowledge search/i },
      { label: /^copilot$/i, heading: /healthcare copilot/i },
      { label: /^meetings$/i, heading: /meeting & handoff briefs/i },
      { label: /^research$/i, heading: /research assistant/i },
      { label: /^workflows$/i, heading: /workflow agent/i },
      { label: /^insights$/i, heading: /productivity & activity/i },
    ];

    for (const { label, heading } of tabs) {
      await page.getByRole("button", { name: label }).click();
      await expect(page.getByRole("heading", { name: heading })).toBeVisible();
    }

    await page.getByRole("button", { name: /discharge med rec/i }).click();
    await expect(
      page.getByRole("button", { name: /start new discharge review/i })
    ).toBeVisible();
  });
});
