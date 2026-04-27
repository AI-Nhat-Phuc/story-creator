import React from 'react'

function DocumentOutline({ headings }) {
  if (!headings || headings.length === 0) {
    return (
      <p className="text-xs text-base-content/40 italic">No headings yet</p>
    )
  }

  return (
    <ul className="space-y-1">
      {headings.map((h, i) => (
        <li
          key={i}
          style={{ paddingLeft: `${(h.level - 1) * 12}px` }}
          className="text-xs text-base-content/70 truncate hover:text-base-content cursor-default"
          title={h.text}
        >
          {h.level === 1 && <span className="font-semibold">{h.text}</span>}
          {h.level === 2 && <span className="font-medium">{h.text}</span>}
          {h.level >= 3 && <span>{h.text}</span>}
        </li>
      ))}
    </ul>
  )
}

export default DocumentOutline
