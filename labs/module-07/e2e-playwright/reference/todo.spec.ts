// REFERENCE SOLUTION for Lab 03. Compare with the spec your agent generates
// into tests/ — don't copy this file; the point is to review the
// agent's output against it (role-based locators, web-first assertions,
// no fixed sleeps, one behaviour per test).
import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('./'); // relative to baseURL (trailing slash matters)
});

test('adds a todo', async ({ page }) => {
  await page.getByPlaceholder('What needs to be done?').fill('Write soft-delete spec');
  await page.getByPlaceholder('What needs to be done?').press('Enter');

  await expect(page.getByTestId('todo-title')).toHaveText(['Write soft-delete spec']);
  await expect(page.getByText('1 item left')).toBeVisible();
});

test('completes a todo and clears completed', async ({ page }) => {
  const input = page.getByPlaceholder('What needs to be done?');
  await input.fill('Review PR');
  await input.press('Enter');
  await input.fill('Update Jira');
  await input.press('Enter');

  await page.getByRole('listitem').filter({ hasText: 'Review PR' }).getByRole('checkbox').check();
  await expect(page.getByText('1 item left')).toBeVisible();

  await page.getByRole('button', { name: 'Clear completed' }).click();
  await expect(page.getByTestId('todo-title')).toHaveText(['Update Jira']);
});

test('filters active and completed', async ({ page }) => {
  const input = page.getByPlaceholder('What needs to be done?');
  for (const t of ['one', 'two']) {
    await input.fill(t);
    await input.press('Enter');
  }
  await page.getByRole('listitem').filter({ hasText: 'one' }).getByRole('checkbox').check();

  await page.getByRole('link', { name: 'Active' }).click();
  await expect(page.getByTestId('todo-title')).toHaveText(['two']);

  await page.getByRole('link', { name: 'Completed' }).click();
  await expect(page.getByTestId('todo-title')).toHaveText(['one']);
});

test('does not add an empty todo', async ({ page }) => {
  await page.getByPlaceholder('What needs to be done?').press('Enter');
  await expect(page.getByTestId('todo-title')).toHaveCount(0);
});
