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
  try {
    const [storiesRes, worldsRes] = await Promise.all([
      fetch(`${base}/stories`, { next: { revalidate: 60 } }),
      fetch(`${base}/worlds`, { next: { revalidate: 60 } }),
    ])
    const storiesJson = storiesRes.ok ? await storiesRes.json() : {}
    const worldsJson = worldsRes.ok ? await worldsRes.json() : {}
    return {
      stories: storiesJson.data ?? [],
      worlds: worldsJson.data ?? [],
    }
  } catch {
    return { stories: [], worlds: [] }
  }
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
