import React, { useEffect } from 'react'

function Toast({ message, type = 'info' }) {
  const typeClasses = {
    success: 'alert-success',
    error: 'alert-error',
    warning: 'alert-warning',
    info: 'alert-info'
  }

  return (
    <div className="toast toast-end toast-top">
      <div className={`alert ${typeClasses[type]} shadow-lg`}>
        <div>
          <span>{message}</span>
        </div>
      </div>
    </div>
  )
}

export default Toast
