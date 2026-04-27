import NovelPage from '../../../../../src/views/NovelPage'
import { getServerLocale, getServerT } from '../../../../../src/i18n/serverI18n'

function getServerApiBase() {
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}/api`
  }
  return 'http://localhost:5000/api'
}

function getBypassHeaders() {
  const bypass =
    process.env.VERCEL_AUTOMATION_BYPASS_SECRET ||
    process.env.VERCEL_BYPASS_SECRET
  return bypass ? { 'x-vercel-protection-bypass': bypass } : {}
}

export async function generateMetadata({ params }) {
  const { worldId } = params
  const t = getServerT()
  try {
    const res = await fetch(
      `${getServerApiBase()}/worlds/${worldId}/novel`,
      { headers: getBypassHeaders(), next: { revalidate: 60 } }
    )
    if (res.ok) {
      const json = await res.json()
      const name = json.data?.title
      if (name) {
        return {
          title: t('meta.novel.titleTemplate').replace('{{name}}', name),
          description: t('meta.novel.descriptionTemplate').replace('{{name}}', name),
        }
      }
    }
  } catch {}
  return {
    title: t('meta.novel.titleFallback'),
    description: t('meta.novel.descriptionFallback'),
  }
}

async function fetchInitialNovelData(worldId) {
  const base = getServerApiBase()
  const headers = getBypassHeaders()
  try {
    const [metaRes, contentRes] = await Promise.all([
      fetch(`${base}/worlds/${worldId}/novel`, { headers, next: { revalidate: 60 } }),
      fetch(`${base}/worlds/${worldId}/novel/content?line_budget=100`, { headers, next: { revalidate: 60 } }),
    ])
    if (!metaRes.ok || !contentRes.ok) return null
    const [metaJson, contentJson] = await Promise.all([metaRes.json(), contentRes.json()])
    return {
      novel: metaJson.data ?? null,
      chapters: metaJson.data?.chapters ?? [],
      contentBlocks: contentJson.data?.blocks ?? [],
      nextCursor: contentJson.data?.next_cursor ?? null,
      hasMore: contentJson.data?.has_more ?? false,
    }
  } catch {
    return null
  }
}

export default async function Page({ params }) {
  const { worldId } = params
  const [initialData, locale] = await Promise.all([
    fetchInitialNovelData(worldId),
    Promise.resolve(getServerLocale()),
  ])
  return <NovelPage initialData={initialData} locale={locale} />
}
