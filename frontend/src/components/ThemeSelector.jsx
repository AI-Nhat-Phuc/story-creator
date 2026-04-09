import React from 'react'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../contexts/ThemeContext'
import { THEME_MODES } from '../utils/themeUtils'

const MODES = [
  { id: THEME_MODES.LIGHT,  labelKey: 'theme.light'  },
  { id: THEME_MODES.DARK,   labelKey: 'theme.dark'   },
  { id: THEME_MODES.CUSTOM, labelKey: 'theme.custom' },
]

const SWATCHES = [
  { key: 'primary',   labelKey: 'theme.primary'    },
  { key: 'secondary', labelKey: 'theme.secondary'  },
  { key: 'accent',    labelKey: 'theme.accent'     },
  { key: 'base100',   labelKey: 'theme.background' },
  { key: 'base200',   labelKey: 'theme.surface'    },
]

const LANGUAGES = [
  { code: 'vi', labelKey: 'theme.vi' },
  { code: 'en', labelKey: 'theme.en' },
]

function ThemeSelector() {
  const { mode, primaryColor, colors, setMode, setPrimaryColor } = useTheme()
  const { t, i18n } = useTranslation()

  const switchLanguage = (lang) => {
    i18n.changeLanguage(lang)
  }

  return (
    <div className="flex flex-col gap-2 p-2">
      {/* Theme mode buttons */}
      <div className="flex gap-1">
        {MODES.map(({ id, labelKey }) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            className={`btn btn-xs flex-1 ${mode === id ? 'btn-primary' : 'btn-ghost'}`}
          >
            {t(labelKey)}
          </button>
        ))}
      </div>

      {/* Color swatches — style={{ backgroundColor }} is intentional (palette preview) */}
      <div className="flex gap-1 justify-center">
        {SWATCHES.map(({ key, labelKey }) => (
          <div
            key={key}
            title={t(labelKey)}
            className="w-6 h-6 rounded-full border border-base-300 flex-shrink-0"
            style={{ backgroundColor: colors[key] }}
          />
        ))}
      </div>

      {/* Custom primary color picker */}
      {mode === THEME_MODES.CUSTOM && (
        <div className="flex items-center gap-2">
          <span className="text-xs opacity-70">{t('theme.primary')}</span>
          <input
            type="color"
            value={primaryColor}
            onChange={(e) => setPrimaryColor(e.target.value)}
            className="w-8 h-8 rounded cursor-pointer border-0 bg-transparent"
          />
        </div>
      )}

      {/* Language toggle */}
      <div className="border-t border-base-300 pt-2 mt-1">
        <p className="text-xs opacity-60 mb-1">{t('theme.language')}</p>
        <div className="flex gap-1">
          {LANGUAGES.map(({ code, labelKey }) => (
            <button
              key={code}
              onClick={() => switchLanguage(code)}
              className={`btn btn-xs flex-1 ${i18n.language === code ? 'btn-primary' : 'btn-ghost'}`}
            >
              {t(labelKey)}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ThemeSelector
