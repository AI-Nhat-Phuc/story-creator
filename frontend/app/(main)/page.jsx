import HomePage from '../../src/views/HomePage'

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
      initialStories: storiesJson.data ?? [],
      initialWorlds: worldsJson.data ?? [],
    }
  } catch {
    return { initialStories: [], initialWorlds: [] }
  }
}

export default async function Page() {
  const { initialStories, initialWorlds } = await fetchDiscoveryData()
  return <HomePage initialStories={initialStories} initialWorlds={initialWorlds} />
}
