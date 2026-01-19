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
    <div className="z-50 fixed inset-0 flex justify-center items-center bg-black/40">
      <div className={`bg-white rounded-lg shadow-lg max-w-lg w-full p-6 relative ${className}`}>
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
