import React from 'react'

/**
 * Shared Tag/Badge component.
 *
 * - Text never wraps inside the tag (whitespace-nowrap).
 * - Multiple tags in a `flex flex-wrap` container will flow to the next row naturally.
 * - Supports DaisyUI badge colors, sizes, and the outline variant.
 * - Optional leading icon (Heroicon component ref).
 * - Renders as <span> by default; pass `as={Link}` (or any element/component) to change.
 *
 * @param {string}  color      – DaisyUI badge color token: 'primary' | 'secondary' | 'success' |
 *                               'warning' | 'error' | 'info' | 'ghost' | 'neutral' | 'accent'
 * @param {string}  size       – 'xs' | 'sm' | 'lg'  (omit for default)
 * @param {boolean} outline    – renders the outline variant
 * @param {React.ElementType} icon – Heroicon component, rendered before children
 * @param {string}  className  – additional Tailwind classes
 * @param {React.ElementType} as – element or component to render as (default: 'span')
 */
function Tag({
  children,
  color,
  size,
  outline = false,
  icon: Icon,
  className = '',
  as: Component = 'span',
  ...props
}) {
  const iconSizeClass = size === 'xs' ? 'w-2.5 h-2.5' : size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'

  const classes = [
    'badge',
    'whitespace-nowrap',
    'py-1',
    color && `badge-${color}`,
    size && `badge-${size}`,
    outline && 'badge-outline',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <Component className={classes} {...props}>
      {Icon && <Icon className={`inline shrink-0 ${iconSizeClass}`} aria-hidden="true" />}
      {children}
    </Component>
  )
}

export default Tag
