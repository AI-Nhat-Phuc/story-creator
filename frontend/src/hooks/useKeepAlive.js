import { useEffect } from 'react'
import api from '../services/api'

/**
 * Silently pings /api/health every `intervalMs` while the browser tab is visible.
 * Keeps the Vercel serverless container warm to prevent cold starts.
 *
 * @param {number} intervalMs - Ping interval in milliseconds (default: 5 minutes)
 */
export function useKeepAlive(intervalMs = 300000) {
  useEffect(() => {
    let intervalId = null

    const ping = () => {
      if (document.visibilityState === 'visible') {
        api.get('/health').catch(() => {})
      }
    }

    const startInterval = () => {
      if (intervalId === null) {
        intervalId = setInterval(ping, intervalMs)
      }
    }

    const stopInterval = () => {
      if (intervalId !== null) {
        clearInterval(intervalId)
        intervalId = null
      }
    }

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        startInterval()
      } else {
        stopInterval()
      }
    }

    // Start only if tab is currently visible
    if (document.visibilityState === 'visible') {
      startInterval()
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      stopInterval()
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [intervalMs])
}
