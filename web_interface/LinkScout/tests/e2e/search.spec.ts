import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Search page (mobile)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search');
  });

  test('has a visible search input wrapper and is accessible', async ({ page }) => {
    // wait for input wrapper
    const wrapper = page.locator('#ls-search-input');
    await expect(wrapper).toBeVisible();

    // inject axe and check a11y for the input area
    await injectAxe(page);
    const violations = await checkA11y(page, '#ls-search-input', undefined, undefined);
    // checkA11y throws on violations in axe-playwright v2; to be safe, ensure wrapper exists
    await expect(page.locator('input[aria-label="Message input"]')).toBeVisible();
  });

  test('can send a message and receive AI reply', async ({ page }) => {
    const input = page.locator('input[aria-label="Message input"]');
    await expect(input).toBeVisible();
    await input.click();
    await input.fill('Playwright test message');
    await input.press('Enter');

    // Wait for AI response text to appear
    await expect(page.locator('text=I received your message')).toBeVisible({ timeout: 8000 });
  });
});
