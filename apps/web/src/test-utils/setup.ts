import '@testing-library/jest-dom'

// Polyfill ResizeObserver for jsdom (needed by cmdk)
if (typeof global.ResizeObserver === 'undefined') {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}
