import { createRef } from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { useFocusTrap } from '../src/hooks/useFocusTrap'

function FocusTrapHarness({ onEscape }: { onEscape?: () => void }) {
  const containerRef = createRef<HTMLDivElement>()
  useFocusTrap(true, containerRef, onEscape)

  return (
    <div ref={containerRef}>
      <button type="button">First</button>
      <button type="button">Last</button>
    </div>
  )
}

describe('useFocusTrap', () => {
  it('closes the active modal when Escape is pressed', () => {
    const onEscape = vi.fn()

    render(<FocusTrapHarness onEscape={onEscape} />)

    fireEvent.keyDown(screen.getByText('First'), { key: 'Escape' })

    expect(onEscape).toHaveBeenCalledTimes(1)
  })

  it('wraps focus when tabbing past the last control', () => {
    render(<FocusTrapHarness />)

    const first = screen.getByText('First')
    const last = screen.getByText('Last')

    expect(first).toHaveFocus()

    last.focus()
    fireEvent.keyDown(last, { key: 'Tab' })

    expect(first).toHaveFocus()
  })
})
