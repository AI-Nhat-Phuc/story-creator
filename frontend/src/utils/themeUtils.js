export const DEFAULT_PRIMARY = '#6366F1'

export const THEME_MODES = {
  LIGHT: 'light',
  DARK: 'dark',
  CUSTOM: 'custom',
}

export const LIGHT_PALETTE = {
  primary:   '#4A90D9',
  secondary: '#6BA3BE',
  accent:    '#F5A623',
  base100:   '#FFFFFF',
  base200:   '#F2F4F6',
}

export const DARK_PALETTE = {
  primary:   '#E2E8F0',
  secondary: '#94A3B8',
  accent:    '#F59E0B',
  base100:   '#1E293B',
  base200:   '#0F172A',
}

export function isValidHex(hex) {
  return /^#[0-9a-fA-F]{6}$/.test(hex)
}

export function hexToHsl(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255
  const g = parseInt(hex.slice(3, 5), 16) / 255
  const b = parseInt(hex.slice(5, 7), 16) / 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const delta = max - min

  let h = 0
  if (delta !== 0) {
    if (max === r) h = ((g - b) / delta) % 6
    else if (max === g) h = (b - r) / delta + 2
    else h = (r - g) / delta + 4
    h = Math.round(h * 60)
    if (h < 0) h += 360
  }

  const l = (max + min) / 2
  const s = delta === 0 ? 0 : delta / (1 - Math.abs(2 * l - 1))

  return { h, s: Math.round(s * 100), l: Math.round(l * 100) }
}

// DaisyUI v4 uses oklch format: "L% C H"
export function hexToOklch(hex) {
  const toLinear = (v) => v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
  const r = toLinear(parseInt(hex.slice(1, 3), 16) / 255)
  const g = toLinear(parseInt(hex.slice(3, 5), 16) / 255)
  const b = toLinear(parseInt(hex.slice(5, 7), 16) / 255)

  // Linear RGB → OKLab (via M1 then cube root then M2)
  const lc = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
  const mc = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
  const sc = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)

  const L = 0.2104542553 * lc + 0.7936177850 * mc - 0.0040720468 * sc
  const a = 1.9779984951 * lc - 2.4285922050 * mc + 0.4505937099 * sc
  const bOk = 0.0259040371 * lc + 0.7827717662 * mc - 0.8086757660 * sc

  const C = Math.sqrt(a * a + bOk * bOk)
  const H = (Math.atan2(bOk, a) * 180 / Math.PI + 360) % 360

  return {
    l: Math.round(L * 10000) / 100,
    c: Math.round(C * 10000) / 10000,
    h: Math.round(H * 100) / 100,
  }
}

function hslToHex(h, s, l) {
  const sN = s / 100
  const lN = l / 100
  const a = sN * Math.min(lN, 1 - lN)
  const f = (n) => {
    const k = (n + h / 30) % 12
    const color = lN - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    return Math.round(255 * color).toString(16).padStart(2, '0')
  }
  return `#${f(0)}${f(8)}${f(4)}`
}

// WCAG relative luminance — byteOffset is the hex string byte position (1, 3, 5)
export function relativeLuminance(hex) {
  const toLinear = (byteOffset) => {
    const v = parseInt(hex.slice(byteOffset, byteOffset + 2), 16) / 255
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
  }
  return 0.2126 * toLinear(1) + 0.7152 * toLinear(3) + 0.0722 * toLinear(5)
}

export function deriveCustomPalette(primaryHex) {
  const { h, s, l } = hexToHsl(primaryHex)
  const secondary = hslToHex(h, Math.max(0, s - 20), Math.min(100, l + 15))
  const accent = hslToHex((h + 30) % 360, Math.min(100, s + 15), l)
  const lum = relativeLuminance(primaryHex)
  const base100 = lum < 0.5 ? '#FFFFFF' : '#1E293B'
  const base200 = lum < 0.5 ? hslToHex(h, 20, 95) : hslToHex(h, 20, 10)
  return { primary: primaryHex, secondary, accent, base100, base200 }
}
