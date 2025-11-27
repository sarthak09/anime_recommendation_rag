// src/setupTests.js
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with all jest-dom matchers
expect.extend(matchers);

// Clean up the DOM after each test (good practice)
afterEach(() => {
  cleanup();
});
