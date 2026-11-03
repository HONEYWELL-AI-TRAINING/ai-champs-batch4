import { defineConfig, devices } from '@playwright/test';

// Target app for Lab 03. Override to point at your own app:
//   BASE_URL=http://localhost:3000 npx playwright test
const baseURL = process.env.BASE_URL ?? 'https://demo.playwright.dev/todomvc/'; // keep the trailing slash

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL,
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
