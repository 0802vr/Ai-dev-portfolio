import { expect, test } from "@playwright/test";

test("лендинг имеет семантическую структуру и доступную форму", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("header")).toBeVisible();
  await expect(page.locator("main")).toBeVisible();
  await expect(page.locator("footer")).toBeVisible();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Создаю цифровые");
  await page.locator('.header-link[href="#contact"]').click();
  await expect(page.getByRole("form", { name: "Форма обратной связи" })).toBeInViewport();
  await expect(page.getByLabel("Email")).toHaveAttribute("type", "email");
});
