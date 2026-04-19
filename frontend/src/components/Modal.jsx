import React, { useEffect } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'

/**
 * Modal component for popup dialogs.
 *
 * Behaviour:
 * - Mobile  : bottom-sheet with dark overlay; body scroll is locked.
 * - Desktop : centred card with no dark overlay; page scroll is preserved
 *             (only the modal card intercepts pointer events).
 *
 * @param {boolean}           open      – whether the modal is visible
 * @param {function}          onClose   – called when the user dismisses the modal
 * @param {string}            title     – optional heading
 * @param {React.ReactNode}   children  – modal body
 * @param {string}            className – extra classes applied to the modal card
 */
export default function Modal({ open, onClose, title, children, className = '' }) {
  // Lock body scroll on mobile only while open
  useEffect(() => {
    if (!open) return
    const isMobile = window.innerWidth < 640
    if (isMobile) {
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  if (!open) return null

  return (
    <>
      {/* ── Mobile: dark full-screen overlay ─────────────────────────── */}
      <div
        className="sm:hidden fixed inset-0 z-40 bg-black/50"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* ── Flex container: bottom-sheet on mobile, centred on desktop ── */}
      {/*    pointer-events-none so the desktop page stays scrollable;    */}
      {/*    the card below re-enables pointer events for itself.         */}
      <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center pointer-events-none">
        <div
          className={[
            // reset pointer events so the card is interactive
            'pointer-events-auto',
            // layout & sizing
            'relative w-full sm:max-w-lg',
            // shape: rounded top on mobile, rounded all on desktop
            'rounded-t-2xl sm:rounded-2xl',
            // colours & depth
            'bg-base-100 text-base-content shadow-2xl',
            // spacing
            'p-6',
            // height constraints
            'max-h-[90dvh] sm:max-h-[85vh] overflow-y-auto',
            // slide-up on mobile
            'mobile-slide-up sm:animate-none',
            className,
          ]
            .filter(Boolean)
            .join(' ')}
          // Prevent clicks inside the card from bubbling to the overlay
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            className="absolute top-3 right-3 btn btn-sm btn-circle btn-ghost"
            onClick={onClose}
            aria-label="Đóng"
          >
            <XMarkIcon className="w-4 h-4" />
          </button>

          {title && (
            <h2 className="mb-4 pr-8 font-bold text-xl">{title}</h2>
          )}

          <div>{children}</div>
        </div>
      </div>
    </>
  )
}
