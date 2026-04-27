import { getServerT } from '../../../src/i18n/serverI18n'
import StoriesPage from '../../../src/views/StoriesPage'

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

export function generateMetadata() {
  const t = getServerT()
  return {
    title: t('meta.stories.title'),
    description: t('meta.stories.description'),
  }
}

async function fetchInitialData() {
  const base = getServerApiBase()
  const headers = getBypassHeaders()
  try {
    const [storiesRes, worldsRes] = await Promise.all([
      fetch(`${base}/stories`, { headers, next: { revalidate: 60 } }),
      fetch(`${base}/worlds`, { headers, next: { revalidate: 60 } }),
    ])
    if (!storiesRes.ok || !worldsRes.ok) return null
    const [storiesJson, worldsJson] = await Promise.all([
      storiesRes.json(),
      worldsRes.json(),
    ])
    return {
      stories: storiesJson.data ?? [],
      worlds: worldsJson.data ?? [],
    }
  } catch {
    return null
  }
}

export default async function Page() {
  const initialData = await fetchInitialData()
  return <StoriesPage initialData={initialData} />
}
