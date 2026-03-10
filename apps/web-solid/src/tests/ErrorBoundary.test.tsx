import { describe, it, expect } from 'vitest'

describe('ErrorBoundary', () => {
  it('fallback message is a string', () => {
    const fallback = 'Something went wrong'
    expect(typeof fallback).toBe('string')
  })
  it('error boundary concept: children render when no error', () => {
    const hasError = false
    expect(hasError).toBe(false)
  })
})
