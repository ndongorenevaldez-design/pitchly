// Responsibility: Render accessible modal content when needed.
import type { ReactNode } from 'react'
import { Button } from './Button'

export function Modal({
  open,
  title,
  children,
  onClose,
}: {
  open: boolean
  title: string
  children: ReactNode
  onClose: () => void
}) {
  if (!open) return null
  return (
    <div className="modal-backdrop" role="presentation">
      <div className="modal" role="dialog" aria-modal="true" aria-label={title}>
        <div className="modal-header">
          <h2>{title}</h2>
          <Button variant="ghost" onClick={onClose} aria-label="Close">
            x
          </Button>
        </div>
        {children}
      </div>
    </div>
  )
}
