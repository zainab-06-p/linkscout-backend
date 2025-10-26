import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'tests/e2e',
  timeout: 30_000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    ignoreHTTPSErrors: true,
    viewport: { width: 375, height: 812 },
    actionTimeout: 5000,
    navigationTimeout: 30000,
  },
  projects: [
    {
      name: 'mobile',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
});
