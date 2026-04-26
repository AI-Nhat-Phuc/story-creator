'use client'

import React, { createContext, useContext, useState, useLayoutEffect } from 'react'
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

function saveToStorage(mode, primaryColor) {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ mode, primaryColor }))
  } catch {
    // localStorage unavailable — silent fail (e.g. private browsing)
  }
}

// DaisyUI v4 uses oklch format: "L% C H"
function hexToDaisyOklch(hex) {
  const { l, c, h } = hexToOklch(hex)
  return `${l}% ${c} ${h}`
}

const CSS_VARS = ['--p', '--pc', '--s', '--sc', '--a', '--ac', '--b1', '--b2']

// Returns DaisyUI oklch for readable text on the given background hex color.
function contrastOklch(hex) {
  return relativeLuminance(hex) > 0.22 ? '0% 0 0' : '100% 0 0'
}

function clearCustomVars() {
  if (typeof document === 'undefined') return
  CSS_VARS.forEach((v) => document.documentElement.style.removeProperty(v))
}

function injectCustomVars(palette) {
  if (typeof document === 'undefined') return
  document.documentElement.style.setProperty('--p', hexToDaisyOklch(palette.primary))
  document.documentElement.style.setProperty('--pc', contrastOklch(palette.primary))
  document.documentElement.style.setProperty('--s', hexToDaisyOklch(palette.secondary))
  document.documentElement.style.setProperty('--sc', contrastOklch(palette.secondary))
  document.documentElement.style.setProperty('--a', hexToDaisyOklch(palette.accent))
  document.documentElement.style.setProperty('--ac', contrastOklch(palette.accent))
  document.documentElement.style.setProperty('--b1', hexToDaisyOklch(palette.base100))
  document.documentElement.style.setProperty('--b2', hexToDaisyOklch(palette.base200))
}

export function getPalette(mode, primaryColor) {
  if (mode === THEME_MODES.LIGHT) return LIGHT_PALETTE
  if (mode === THEME_MODES.DARK) return DARK_PALETTE
  return deriveCustomPalette(primaryColor)
}

// Accept a pre-computed palette to avoid double-deriving in custom mode
function applyTheme(mode, palette) {
  if (typeof document === 'undefined') return
  const html = document.documentElement
  if (mode === THEME_MODES.LIGHT) {
    html.setAttribute('data-theme', 'sc-light')
    clearCustomVars()
  } else if (mode === THEME_MODES.DARK) {
    html.setAttribute('data-theme', 'sc-dark')
    clearCustomVars()
  } else {
    const base = relativeLuminance(palette.base100) > 0.22 ? 'sc-light' : 'sc-dark'
    html.setAttribute('data-theme', base)
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
