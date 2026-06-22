// Responsibility: Render consistent command buttons.
import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  icon?: ReactNode
}

export function Button({
  className = '',
  variant = 'primary',
  icon,
  children,
  ...props
}: Props) {
  return (
    <button className={`btn btn-${variant} ${className}`} type="button" {...props}>
      {icon}
      <span>{children}</span>
    </button>
  )
}
