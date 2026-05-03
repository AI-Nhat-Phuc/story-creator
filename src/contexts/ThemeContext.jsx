'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import {
  LIGHT_PALETTE,
  DARK_PALETTE,
  DEFAULT_PRIMARY,
  THEME_MODES,
  isValidHex,
  deriveCustomPalette,
  hexToOklch,
  relativeLuminance,
} from '../utils/themeUtils'

const ThemeContext = createContext(null)

const STORAGE_KEY = 'sc_theme'

function loadFromStorage() {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function saveToStorage(mode, primaryColor, cssVars, base) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode, primaryColor, cssVars, base }))
  } catch {
    // localStorage unavailable — silent fail (e.g. private browsing)
  }
}

// DaisyUI v4 uses oklch format: "L% C H"
function hexToDaisyOklch(hex) {
  const { l, c, h } = hexToOklch(hex)
  return `${l}% ${c} ${h}`
}

const CSS_VARS = ['--p', '--pc', '--s', '--sc', '--a', '--ac', '--b1', '--b2', '--n', '--nc']

// Returns DaisyUI oklch for readable text on the given background hex color.
function contrastOklch(hex) {
  return relativeLuminance(hex) > 0.22 ? '0% 0 0' : '100% 0 0'
}

function clearCustomVars() {
  if (typeof document === 'undefined') return
  CSS_VARS.forEach((v) => document.documentElement.style.removeProperty(v))
}

function buildCustomVars(palette) {
  return {
    '--p':  hexToDaisyOklch(palette.primary),
    '--pc': contrastOklch(palette.primary),
    '--s':  hexToDaisyOklch(palette.secondary),
    '--sc': contrastOklch(palette.secondary),
    '--a':  hexToDaisyOklch(palette.accent),
    '--ac': contrastOklch(palette.accent),
    '--b1': hexToDaisyOklch(palette.base100),
    '--n':  hexToDaisyOklch(palette.base100),
    '--b2': hexToDaisyOklch(palette.base200),
  }
}

function injectCustomVars(palette) {
  if (typeof document === 'undefined') return null
  const vars = buildCustomVars(palette)
  Object.entries(vars).forEach(([k, v]) => document.documentElement.style.setProperty(k, v))
  return vars
}

export function getPalette(mode, primaryColor) {
  if (mode === THEME_MODES.LIGHT) return LIGHT_PALETTE
  if (mode === THEME_MODES.DARK) return DARK_PALETTE
  return deriveCustomPalette(primaryColor)
}

// Accept a pre-computed palette to avoid double-deriving in custom mode.
// Returns { cssVars, base } for custom mode (used to persist to storage).
function applyTheme(mode, palette) {
  if (typeof document === 'undefined') return {}
  const html = document.documentElement
  if (mode === THEME_MODES.LIGHT) {
    html.setAttribute('data-theme', 'sc-light')
    clearCustomVars()
    return {}
  } else if (mode === THEME_MODES.DARK) {
    html.setAttribute('data-theme', 'sc-dark')
    clearCustomVars()
    return {}
  } else {
    const base = relativeLuminance(palette.base100) > 0.22 ? 'sc-light' : 'sc-dark'
    html.setAttribute('data-theme', base)
    const cssVars = injectCustomVars(palette)
    return { cssVars, base }
  }
}

function getDefaultState() {
  return { mode: THEME_MODES.LIGHT, primaryColor: DEFAULT_PRIMARY }
}

function getStoredState() {
  const saved = loadFromStorage()
  if (!saved) return null
  const mode = saved.mode ?? THEME_MODES.LIGHT
  const raw = saved.primaryColor ?? DEFAULT_PRIMARY
  const primaryColor = isValidHex(raw) ? raw : DEFAULT_PRIMARY
  return { mode, primaryColor }
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside ThemeProvider')
  return ctx
}

export function ThemeProvider({ children }) {
  // Initialise with defaults so the SSR HTML matches the client's first
  // render. The user's saved theme is applied in the post-mount effect
  // below — any theme-driven UI re-renders without a hydration warning.
  const [{ mode, primaryColor }, setTheme] = useState(getDefaultState)

  useEffect(() => {
    const stored = getStoredState()
    const state = stored ?? { mode, primaryColor }
    if (stored) setTheme(stored)
    const palette = getPalette(state.mode, state.primaryColor)
    const { cssVars, base } = applyTheme(state.mode, palette)
    // Persist computed vars so the inline script can apply them next load
    if (state.mode === THEME_MODES.CUSTOM && cssVars) {
      saveToStorage(state.mode, state.primaryColor, cssVars, base)
    }
    // Reveal body (was hidden by inline script for custom theme without stored vars)
    document.body.style.removeProperty('visibility')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function setMode(newMode) {
    setTheme((prev) => ({ ...prev, mode: newMode }))
    applyTheme(newMode, getPalette(newMode, primaryColor))
    saveToStorage(newMode, primaryColor, null, null)
  }

  function setPrimaryColor(hex) {
    const safe = isValidHex(hex) ? hex : DEFAULT_PRIMARY
    const palette = deriveCustomPalette(safe)
    setTheme({ mode: THEME_MODES.CUSTOM, primaryColor: safe })
    const { cssVars, base } = applyTheme(THEME_MODES.CUSTOM, palette)
    saveToStorage(THEME_MODES.CUSTOM, safe, cssVars, base)
  }

  const colors = getPalette(mode, primaryColor)

  return (
    <ThemeContext.Provider value={{ mode, primaryColor, colors, setMode, setPrimaryColor }}>
      {children}
    </ThemeContext.Provider>
  )
}
