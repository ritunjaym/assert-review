import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Polyfill ResizeObserver for jsdom (needed by cmdk)
if (typeof global.ResizeObserver === 'undefined') {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}

// Mock SWR globally to prevent refreshInterval timers from keeping the event loop alive
vi.mock('swr', () => ({
  default: vi.fn(() => ({ data: undefined, error: undefined, isLoading: false })),
  mutate: vi.fn(),
}))

// Mock Next.js router modules (they hang in jsdom without a router provider)
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), refresh: vi.fn(), back: vi.fn() }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
  redirect: vi.fn(),
}))

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: unknown }) => {
    const React = require('react')
    return React.createElement('a', { href, ...props }, children)
  },
}))
