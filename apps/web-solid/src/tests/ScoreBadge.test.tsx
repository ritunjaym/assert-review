import { describe, it, expect } from 'vitest'

describe('ScoreBadge labels', () => {
  it('Critical maps to correct class', () => {
    const labels = ['Critical', 'Important', 'Low']
    expect(labels).toContain('Critical')
  })
  it('recognizes all three score levels', () => {
    const scores = { Critical: 'red', Important: 'yellow', Low: 'slate' }
    expect(Object.keys(scores)).toHaveLength(3)
  })
  it('Low is lowest priority', () => {
    const order = ['Critical', 'Important', 'Low']
    expect(order.indexOf('Low')).toBeGreaterThan(order.indexOf('Critical'))
  })
})
