import { describe, it, expect } from 'vitest'
import {
  deriveCustomPalette,
  isValidHex,
  hexToHsl,
  LIGHT_PALETTE,
  DARK_PALETTE,
  DEFAULT_PRIMARY,
} from './themeUtils'

// B-3: Light theme has exactly 5 fixed colors
describe('LIGHT_PALETTE (B-3)', () => {
  it('has exactly 5 color slots', () => {
    const keys = Object.keys(LIGHT_PALETTE)
    expect(keys).toHaveLength(5)
    expect(keys).toEqual(expect.arrayContaining(['primary', 'secondary', 'accent', 'base100', 'base200']))
  })

  it('primary is #4A90D9', () => {
    expect(LIGHT_PALETTE.primary.toLowerCase()).toBe('#4a90d9')
  })

  it('base-100 is #FFFFFF (white)', () => {
    expect(LIGHT_PALETTE.base100.toLowerCase()).toBe('#ffffff')
  })

  it('base-200 is a light gray', () => {
    expect(LIGHT_PALETTE.base200.toLowerCase()).toBe('#f2f4f6')
  })
})

// B-4: Dark theme has exactly 5 fixed colors
describe('DARK_PALETTE (B-4)', () => {
  it('has exactly 5 color slots', () => {
    const keys = Object.keys(DARK_PALETTE)
    expect(keys).toHaveLength(5)
    expect(keys).toEqual(expect.arrayContaining(['primary', 'secondary', 'accent', 'base100', 'base200']))
  })

  it('base-100 is dark navy #1E293B', () => {
    expect(DARK_PALETTE.base100.toLowerCase()).toBe('#1e293b')
  })

  it('base-200 is near black #0F172A', () => {
    expect(DARK_PALETTE.base200.toLowerCase()).toBe('#0f172a')
  })
})

// B-5 / BR-4: Custom palette algorithm
describe('deriveCustomPalette (B-5)', () => {
  it('returns exactly 5 keys', () => {
    const palette = deriveCustomPalette('#6366F1')
    expect(Object.keys(palette)).toHaveLength(5)
    expect(Object.keys(palette)).toEqual(
      expect.arrayContaining(['primary', 'secondary', 'accent', 'base100', 'base200'])
    )
  })

  it('primary equals the input hex (BR-4)', () => {
    const palette = deriveCustomPalette('#6366F1')
    expect(palette.primary.toLowerCase()).toBe('#6366f1')
  })

  it('is deterministic — same input always gives same output (BR-4)', () => {
    const a = deriveCustomPalette('#E74C3C')
    const b = deriveCustomPalette('#E74C3C')
    expect(a).toEqual(b)
  })

  it('all 5 output values are valid hex strings', () => {
    const palette = deriveCustomPalette('#6366F1')
    const hexPattern = /^#[0-9a-fA-F]{6}$/
    for (const val of Object.values(palette)) {
      expect(val).toMatch(hexPattern)
    }
  })

  it('base-100 is white when primary is dark (luminance < 0.5)', () => {
    // #1a1a2e is very dark
    const palette = deriveCustomPalette('#1A1A2E')
    expect(palette.base100.toLowerCase()).toBe('#ffffff')
  })

  it('base-100 is dark when primary is light (luminance >= 0.5)', () => {
    // #FFFFFF is pure white
    const palette = deriveCustomPalette('#FFFFFF')
    expect(palette.base100.toLowerCase()).toBe('#1e293b')
  })

  it('accent has hue shifted +30 degrees from primary', () => {
    const { h: pH } = hexToHsl('#6366F1')
    const palette = deriveCustomPalette('#6366F1')
    const { h: aH } = hexToHsl(palette.accent)
    const diff = ((aH - pH) + 360) % 360
    expect(diff).toBeCloseTo(30, 0)
  })
})

// BR-2: Hex validation
describe('isValidHex (BR-2)', () => {
  it('accepts valid 6-digit hex with #', () => {
    expect(isValidHex('#6366F1')).toBe(true)
    expect(isValidHex('#ffffff')).toBe(true)
    expect(isValidHex('#000000')).toBe(true)
  })

  it('rejects 3-digit shorthand', () => {
    expect(isValidHex('#fff')).toBe(false)
  })

  it('rejects hex without #', () => {
    expect(isValidHex('6366F1')).toBe(false)
  })

  it('rejects empty string', () => {
    expect(isValidHex('')).toBe(false)
  })

  it('rejects non-hex characters', () => {
    expect(isValidHex('#GGGGGG')).toBe(false)
  })
})

// EC-2: Invalid hex falls back to DEFAULT_PRIMARY
describe('DEFAULT_PRIMARY (EC-2)', () => {
  it('is #6366F1 (indigo)', () => {
    expect(DEFAULT_PRIMARY.toLowerCase()).toBe('#6366f1')
  })
})

// BR-1: No 6th color slot
describe('BR-1 — no 6th color slot', () => {
  it('deriveCustomPalette does not return more than 5 colors', () => {
    const palette = deriveCustomPalette('#4A90D9')
    expect(Object.keys(palette).length).toBe(5)
  })
})
