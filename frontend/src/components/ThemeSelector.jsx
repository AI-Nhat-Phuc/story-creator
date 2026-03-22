import React from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { THEME_MODES } from '../utils/themeUtils'

const MODES = [
  { id: THEME_MODES.LIGHT,  label: 'Light'  },
  { id: THEME_MODES.DARK,   label: 'Dark'   },
  { id: THEME_MODES.CUSTOM, label: 'Custom' },
]

const SWATCHES = [
  { key: 'primary',   label: 'Primary'    },
  { key: 'secondary', label: 'Secondary'  },
  { key: 'accent',    label: 'Accent'     },
  { key: 'base100',   label: 'Background' },
  { key: 'base200',   label: 'Surface'    },
]

function ThemeSelector() {
  const { mode, primaryColor, colors, setMode, setPrimaryColor } = useTheme()

  return (
    <div className="flex flex-col gap-2 p-2">
      <div className="flex gap-1">
        {MODES.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            className={`btn btn-xs flex-1 ${mode === id ? 'btn-primary' : 'btn-ghost'}`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="flex gap-1 justify-center">
        {SWATCHES.map(({ key, label }) => (
          <div
            key={key}
            title={label}
            className="w-6 h-6 rounded-full border border-base-300 flex-shrink-0"
            style={{ backgroundColor: colors[key] }}
          />
        ))}
      </div>

      {mode === THEME_MODES.CUSTOM && (
        <div className="flex items-center gap-2">
          <span className="text-xs opacity-70">Primary</span>
          <input
            type="color"
            value={primaryColor}
            onChange={(e) => setPrimaryColor(e.target.value)}
            className="w-8 h-8 rounded cursor-pointer border-0 bg-transparent"
          />
        </div>
      )}
    </div>
  )
}

export default ThemeSelector
