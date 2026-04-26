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
    // truncate = white-space: nowrap + overflow-hidden + text-ellipsis.
    // Combined with max-w-full it lets a tag shrink and clip with "…"
    // when its content (e.g. a long story title) would otherwise push
    // the parent flex container past the viewport. min-w-0 is required
    // for the shrink to actually take effect inside a flex-wrap parent.
    'truncate',
    'max-w-full',
    'min-w-0',
    'py-1',
    color && `badge-${color}`,
    size && `badge-${size}`,
    outline && 'badge-outline',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  // If a string was passed as children, use it as the default title so
  // hover/long-press reveals the full text when truncate clips it.
  const tooltip = props.title ?? (typeof children === 'string' ? children : undefined)

  return (
    <Component className={classes} title={tooltip} {...props}>
      {Icon && <Icon className={`inline shrink-0 ${iconSizeClass}`} aria-hidden="true" />}
      {children}
    </Component>
  )
}

export default Tag
