import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import vi from './locales/vi.json'
import en from './locales/en.json'

export const LANG_KEY = 'sc_lang'

function readInitialLang() {
  if (typeof document === 'undefined') return 'vi'
  // Prefer cookie (also readable by Server Components) over localStorage so
  // both render paths converge on the same locale.
  const cookieMatch = document.cookie.match(/(?:^|;\s*)sc_lang=([^;]+)/)
  if (cookieMatch) return decodeURIComponent(cookieMatch[1])
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem(LANG_KEY)
    if (stored) return stored
  }
  return 'vi'
}

i18n
  .use(initReactI18next)
  .init({
    resources: {
      vi: { translation: vi },
      en: { translation: en },
    },
    lng: readInitialLang(),
    fallbackLng: 'vi',
    interpolation: { escapeValue: false },
  })

const persistLang = (lang) => {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(LANG_KEY, lang)
  }
  if (typeof document !== 'undefined') {
    // 1 year, lax — only the user's own browser ever sees it.
    document.cookie = `sc_lang=${encodeURIComponent(lang)}; path=/; max-age=31536000; samesite=lax`
  }
}

i18n.on('languageChanged', persistLang)

export default i18n
