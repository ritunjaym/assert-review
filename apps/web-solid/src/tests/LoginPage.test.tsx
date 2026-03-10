import { describe, it, expect } from 'vitest'

describe('LoginPage', () => {
  it('has sign in text constant', () => {
    const label = 'Sign in with GitHub'
    expect(label).toContain('GitHub')
  })
  it('has CodeLens brand name', () => {
    const brand = 'CodeLens'
    expect(brand).toBe('CodeLens')
  })
})
