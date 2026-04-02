import React from 'react'
import { SparklesIcon } from '@heroicons/react/24/outline'
import LoadingSpinner from '../LoadingSpinner'

function GptToolsPanel({
  selectionLength,
  isLoading,
  suggestions,
  onParaphrase,
  onExpand,
  onApply,
  onClear,
}) {
  const canUseGpt = selectionLength >= 10

  return (
    <div className="space-y-3">
      <div className="text-xs font-semibold text-base-content/60 uppercase tracking-wider">
        GPT Tools
      </div>

      <div className="flex flex-col gap-2">
        <button
          onClick={onParaphrase}
          disabled={!canUseGpt || isLoading}
          className="btn btn-sm btn-outline btn-accent w-full justify-start gap-2"
        >
          <SparklesIcon className="w-4 h-4" />
          Paraphrase
        </button>
        <button
          onClick={onExpand}
          disabled={!canUseGpt || isLoading}
          className="btn btn-sm btn-outline btn-accent w-full justify-start gap-2"
        >
          <SparklesIcon className="w-4 h-4" />
          Expand
        </button>
      </div>

      {!canUseGpt && (
        <p className="text-xs text-base-content/40 italic">
          Select ≥ 10 characters to enable
        </p>
      )}

      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-base-content/60">
          <LoadingSpinner size="sm" />
          Generating…
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-base-content/60">Suggestions</span>
            <button onClick={onClear} className="btn btn-ghost btn-xs">Clear</button>
          </div>
          {suggestions.map((s, i) => (
            <div key={i} className="bg-base-200 rounded p-2 text-sm space-y-1">
              <p className="text-base-content line-clamp-3">{s}</p>
              <button
                onClick={() => onApply(s)}
                className="btn btn-xs btn-primary w-full"
              >
                Apply
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default GptToolsPanel
