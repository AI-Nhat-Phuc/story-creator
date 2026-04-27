import DiscoverySection from '../../src/components/discovery/DiscoverySection'
import HomeAuthGate from '../../src/views/HomeAuthGate'
import { getServerLocale, getServerT } from '../../src/i18n/serverI18n'

export async function generateMetadata() {
  const t = getServerT()
  return {
    title: t('meta.home.title'),
    description: t('meta.home.description'),
  }
}

function getServerApiBase() {
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}/api`
  }
  return 'http://localhost:5000/api'
}

async function fetchDiscoveryData() {
  const base = getServerApiBase()
  // Vercel Deployment Protection (preview URLs) blocks unauthenticated
  // requests to the deployment. Forward the bypass secret when present so
  // a Next.js Server Component can call its sibling Flask function.
  const bypass = process.env.VERCEL_AUTOMATION_BYPASS_SECRET
    || process.env.VERCEL_BYPASS_SECRET
  const headers = bypass ? { 'x-vercel-protection-bypass': bypass } : {}

  const safeFetch = async (url) => {
    try {
      const res = await fetch(url, { headers, next: { revalidate: 60 } })
      if (!res.ok) {
        console.error(`[discovery] ${url} -> HTTP ${res.status}`)
        return []
      }
      const json = await res.json()
      return json.data ?? []
    } catch (err) {
      console.error(`[discovery] ${url} -> ${err?.message || err}`)
      return []
    }
  }

  const [stories, worlds] = await Promise.all([
    safeFetch(`${base}/stories`),
    safeFetch(`${base}/worlds`),
  ])
  return { stories, worlds }
}

export default async function Page() {
  const [{ stories, worlds }, locale] = await Promise.all([
    fetchDiscoveryData(),
    Promise.resolve(getServerLocale()),
  ])

  return (
    <HomeAuthGate>
      <DiscoverySection stories={stories} worlds={worlds} locale={locale} />
    </HomeAuthGate>
  )
}
