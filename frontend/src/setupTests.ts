import '@testing-library/jest-dom';

// Polyfill performance.now for environments where it's not available (some Node versions/jsdom setups)
if (typeof (globalThis as any).performance === 'undefined') {
	(globalThis as any).performance = {
		now: () => Date.now(),
	};
}
import '@testing-library/jest-dom'
