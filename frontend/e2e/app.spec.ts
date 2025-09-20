import { test, expect } from "@playwright/test";

test("upload page renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Recognize your wine")).toBeVisible();
  await expect(page.getByText("Analyze label")).toBeVisible();
});
