import { useTranslation } from 'react-i18next'

/**
 * Returns a localized page title for dynamic routes.
 * When entityName is provided, uses titleTemplate with { name }.
 * When entityName is absent (loading or not found), uses titleFallback.
 *
 * For static routes, call t('meta.X.title') directly instead.
 */
export function usePageTitle(metaKey, entityName) {
  const { t } = useTranslation()
  return entityName
    ? t(`meta.${metaKey}.titleTemplate`, { name: entityName })
    : t(`meta.${metaKey}.titleFallback`)
}
