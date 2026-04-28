import { getServerT } from '../../../src/i18n/serverI18n'
import WorldsPage from '../../../src/views/WorldsPage'

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
    title: t('meta.worlds.title'),
    description: t('meta.worlds.description'),
  }
}

async function fetchInitialWorlds() {
  try {
    const res = await fetch(
      `${getServerApiBase()}/worlds`,
      { headers: getBypassHeaders(), next: { revalidate: 60 } }
    )
    if (!res.ok) return null
    const json = await res.json()
    return json.data ?? null
  } catch {
    return null
  }
}

export default async function Page() {
  const initialWorlds = await fetchInitialWorlds()
  return <WorldsPage initialWorlds={initialWorlds} />
}
