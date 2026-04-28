'use client'

import React, { useState } from 'react'
import { SparklesIcon, EyeIcon, CheckIcon } from '@heroicons/react/24/outline'
import LoadingSpinner from '../LoadingSpinner'

function GptToolsPanel({
  selectionLength,
  isLoading,
  suggestions,
  userCanUseGpt,
  onParaphrase,
  onExpand,
  onApply,
  onClear,
}) {
  const canUseGpt = userCanUseGpt && selectionLength >= 10
  const [previewIdx, setPreviewIdx] = useState(null)

  function closePreview() {
    setPreviewIdx(null)
  }

  function handleApply(s) {
    closePreview()
    onApply(s)
  }

  return (
    <div className="space-y-3">
      <div className="text-xs font-semibold text-base-content/60 uppercase tracking-wider">
        Công cụ GPT
      </div>

      <div className="flex flex-col gap-2">
        <button
          onMouseDown={(e) => { e.preventDefault(); onParaphrase() }}
          disabled={!canUseGpt || isLoading}
          className="btn btn-sm btn-outline btn-accent w-full justify-start gap-2"
        >
          <SparklesIcon className="w-4 h-4" />
          Diễn đạt lại
        </button>
        <button
          onMouseDown={(e) => { e.preventDefault(); onExpand() }}
          disabled={!canUseGpt || isLoading}
          className="btn btn-sm btn-outline btn-accent w-full justify-start gap-2"
        >
          <SparklesIcon className="w-4 h-4" />
          Mở rộng
        </button>
      </div>

      {!userCanUseGpt && (
        <p className="text-xs text-base-content/40 italic">
          Tính năng GPT chưa được kích hoạt cho tài khoản của bạn
        </p>
      )}
      {userCanUseGpt && !canUseGpt && (
        <p className="text-xs text-base-content/40 italic">
          Chọn ≥ 10 ký tự để sử dụng
        </p>
      )}

      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-base-content/60">
          <LoadingSpinner size="sm" />
          Đang tạo…
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-base-content/60">Gợi ý</span>
            <button onMouseDown={(e) => { e.preventDefault(); onClear() }} className="btn btn-ghost btn-xs">Xóa</button>
          </div>
          {suggestions.map((s, i) => (
            <div key={i} className="bg-base-200 rounded p-2 text-sm space-y-1">
              <p className="text-base-content line-clamp-3">{s}</p>
              <div className="flex gap-1 justify-end">
                <button
                  onMouseDown={(e) => { e.preventDefault(); setPreviewIdx(i) }}
                  className="btn btn-xs btn-ghost gap-1"
                  title="Xem trước"
                >
                  <EyeIcon className="w-3.5 h-3.5" />
                  <span>Xem trước</span>
                </button>
                <button
                  onMouseDown={(e) => { e.preventDefault(); handleApply(s) }}
                  className="btn btn-xs btn-primary btn-square"
                  title="Áp dụng"
                >
                  <CheckIcon className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Preview modal */}
      {previewIdx !== null && suggestions[previewIdx] !== undefined && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) closePreview()
          }}
        >
          <div className="bg-base-100 rounded-xl shadow-2xl w-full max-w-sm flex flex-col gap-4 p-4 max-h-[70vh]">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-sm">Xem trước</span>
              <button
                onMouseDown={(e) => { e.preventDefault(); closePreview() }}
                className="btn btn-ghost btn-xs btn-circle"
              >
                ✕
              </button>
            </div>
            <p className="text-sm text-base-content leading-relaxed overflow-y-auto whitespace-pre-wrap flex-1">
              {suggestions[previewIdx]}
            </p>
            <button
              onMouseDown={(e) => { e.preventDefault(); handleApply(suggestions[previewIdx]) }}
              className="btn btn-primary btn-sm w-full"
            >
              Áp dụng
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default GptToolsPanel
