import { cookies } from 'next/headers'
import vi from './locales/vi.json'
import en from './locales/en.json'

const RESOURCES = { vi, en }

/**
 * Reads the user's chosen locale from the `sc_lang` cookie (set by
 * frontend/src/i18n/index.js whenever the user toggles language). Falls back
 * to the default Vietnamese locale when no cookie is present.
 */
export function getServerLocale() {
  try {
    const value = cookies().get('sc_lang')?.value
    if (value && RESOURCES[value]) return value
  } catch {
    // Outside a request scope — return default.
  }
  return 'vi'
}

/**
 * Server-side translator. Reads the locale JSON directly (no react-i18next).
 * Used inside Server Components where hooks aren't available. Resolves the
 * locale from the cookie automatically when none is passed.
 */
export function getServerT(locale) {
  const dict = RESOURCES[locale ?? getServerLocale()] || RESOURCES.vi
  return function t(key) {
    return key.split('.').reduce((obj, k) => (obj == null ? obj : obj[k]), dict) ?? key
  }
}
