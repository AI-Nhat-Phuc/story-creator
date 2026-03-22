import React, { createContext, useContext, useState, useLayoutEffect } from 'react'
import {
  LIGHT_PALETTE,
  DARK_PALETTE,
  DEFAULT_PRIMARY,
  THEME_MODES,
  isValidHex,
  deriveCustomPalette,
  hexToHsl,
} from '../utils/themeUtils'

const ThemeContext = createContext(null)

const STORAGE_KEY = 'sc_theme'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function saveToStorage(mode, primaryColor) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode, primaryColor }))
  } catch {
    // localStorage unavailable — silent fail (e.g. private browsing)
  }
}

// DaisyUI reads HSL as "H S% L%" without the hsl() wrapper
function hexToDaisyHsl(hex) {
  const { h, s, l } = hexToHsl(hex)
  return `${h} ${s}% ${l}%`
}

const CSS_VARS = ['--p', '--s', '--a', '--b1', '--b2']

function clearCustomVars() {
  CSS_VARS.forEach((v) => document.documentElement.style.removeProperty(v))
}

function injectCustomVars(palette) {
  document.documentElement.style.setProperty('--p', hexToDaisyHsl(palette.primary))
  document.documentElement.style.setProperty('--s', hexToDaisyHsl(palette.secondary))
  document.documentElement.style.setProperty('--a', hexToDaisyHsl(palette.accent))
  document.documentElement.style.setProperty('--b1', hexToDaisyHsl(palette.base100))
  document.documentElement.style.setProperty('--b2', hexToDaisyHsl(palette.base200))
}

export function getPalette(mode, primaryColor) {
  if (mode === THEME_MODES.LIGHT) return LIGHT_PALETTE
  if (mode === THEME_MODES.DARK) return DARK_PALETTE
  return deriveCustomPalette(primaryColor)
}

// Accept a pre-computed palette to avoid double-deriving in custom mode
function applyTheme(mode, palette) {
  const html = document.documentElement
  if (mode === THEME_MODES.LIGHT) {
    html.setAttribute('data-theme', 'sc-light')
    clearCustomVars()
  } else if (mode === THEME_MODES.DARK) {
    html.setAttribute('data-theme', 'sc-dark')
    clearCustomVars()
  } else {
    html.setAttribute('data-theme', 'sc-light')
    injectCustomVars(palette)
  }
}

function getInitialState() {
  const saved = loadFromStorage()
  const mode = saved?.mode ?? THEME_MODES.LIGHT
  const raw = saved?.primaryColor ?? DEFAULT_PRIMARY
  const primaryColor = isValidHex(raw) ? raw : DEFAULT_PRIMARY
  return { mode, primaryColor }
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside ThemeProvider')
  return ctx
}

export function ThemeProvider({ children }) {
  const [{ mode, primaryColor }, setTheme] = useState(getInitialState)

  // useLayoutEffect runs before paint — prevents flash of unstyled theme
  useLayoutEffect(() => {
    applyTheme(mode, getPalette(mode, primaryColor))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function setMode(newMode) {
    setTheme((prev) => ({ ...prev, mode: newMode }))
    applyTheme(newMode, getPalette(newMode, primaryColor))
    saveToStorage(newMode, primaryColor)
  }

  function setPrimaryColor(hex) {
    const safe = isValidHex(hex) ? hex : DEFAULT_PRIMARY
    const palette = deriveCustomPalette(safe)
    setTheme({ mode: THEME_MODES.CUSTOM, primaryColor: safe })
    applyTheme(THEME_MODES.CUSTOM, palette)
    saveToStorage(THEME_MODES.CUSTOM, safe)
  }

  const colors = getPalette(mode, primaryColor)

  return (
    <ThemeContext.Provider value={{ mode, primaryColor, colors, setMode, setPrimaryColor }}>
      {children}
    </ThemeContext.Provider>
  )
}
