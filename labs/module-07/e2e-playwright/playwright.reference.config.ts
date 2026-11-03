import { defineConfig } from '@playwright/test';
import base from './playwright.config';

// Runs the known-good spec in reference/ (Lab 03, step 7).
export default defineConfig({ ...base, testDir: './reference' });
