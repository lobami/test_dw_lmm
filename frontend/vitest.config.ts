import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Use happy-dom to avoid jsdom/window performance issues in certain Node versions
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./src/setupTests.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
  },
});
