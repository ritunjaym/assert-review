import { render } from '@solidjs/testing-library'
import { ScoreBadge } from '../components/ScoreBadge'
import { describe, it, expect } from 'vitest'

describe('ScoreBadge', () => {
  it('renders Critical with red styling', () => {
    const { getByText } = render(() => <ScoreBadge label="Critical" />)
    const badge = getByText('Critical')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('red')
  })

  it('renders Important with yellow styling', () => {
    const { getByText } = render(() => <ScoreBadge label="Important" />)
    expect(getByText('Important').className).toContain('yellow')
  })

  it('renders Low with slate styling', () => {
    const { getByText } = render(() => <ScoreBadge label="Low" />)
    expect(getByText('Low').className).toContain('slate')
  })
})
