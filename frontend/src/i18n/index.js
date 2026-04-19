import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import vi from './locales/vi.json'
import en from './locales/en.json'

export const LANG_KEY = 'sc_lang'

i18n
  .use(initReactI18next)
  .init({
    resources: {
      vi: { translation: vi },
      en: { translation: en },
    },
    lng: (typeof localStorage !== 'undefined' ? localStorage.getItem(LANG_KEY) : null) ?? 'vi',
    fallbackLng: 'vi',
    interpolation: { escapeValue: false },
  })

const persistLang = (lang) => {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(LANG_KEY, lang)
  }
}

i18n.on('languageChanged', persistLang)

export default i18n
