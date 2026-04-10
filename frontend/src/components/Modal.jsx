import React from 'react';

/**
 * Modal component for popup dialogs
 * @param {boolean} open - Whether the modal is open
 * @param {function} onClose - Function to close the modal
 * @param {string} title - Modal title
 * @param {React.ReactNode} children - Modal content
 * @param {string} className - Additional classes
 */
export default function Modal({ open, onClose, title, children, className = '' }) {
  if (!open) return null;
  return (
    <div className="z-50 fixed inset-0 flex justify-center items-end sm:items-center bg-black/40">
      <div className={`bg-base-100 rounded-t-2xl rounded-b-none sm:rounded-lg shadow-lg sm:max-w-lg w-full p-6 relative mt-[100px] sm:mt-0 max-h-[calc(100vh-100px)] sm:max-h-[85vh] overflow-y-auto mobile-slide-up sm:animate-none ${className}`}>
        <button
          className="top-2 right-2 absolute btn btn-sm btn-circle btn-ghost"
          onClick={onClose}
          aria-label="Đóng"
        >
          ✕
        </button>
        {title && <h2 className="mb-4 font-bold text-xl">{title}</h2>}
        <div>{children}</div>
      </div>
    </div>
  );
}
