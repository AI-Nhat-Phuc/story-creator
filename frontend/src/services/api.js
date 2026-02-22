import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://localhost:5000/api')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach auth token to every request (module-level so it's active before any useEffect)
api.interceptors.request.use(
  (config) => {
    const authToken = localStorage.getItem('auth_token')
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Worlds API
export const worldsAPI = {
  getAll: () => api.get('/worlds'),
  getById: (id) => api.get(`/worlds/${id}`),
  create: (data) => api.post('/worlds', data),
  update: (id, data) => api.put(`/worlds/${id}`, data),
  delete: (id) => api.delete(`/worlds/${id}`),
  getCharacters: (id) => api.get(`/worlds/${id}/characters`),
  getStories: (id) => api.get(`/worlds/${id}/stories`),
  getLocations: (id) => api.get(`/worlds/${id}/locations`),
  autoLinkStories: (id) => api.post(`/worlds/${id}/auto-link-stories`),
  deleteEntity: (worldId, entityId) => api.delete(`/worlds/${worldId}/entities/${entityId}`),
  deleteLocation: (worldId, locationId) => api.delete(`/worlds/${worldId}/locations/${locationId}`),
}

// Stories API
export const storiesAPI = {
  getAll: () => api.get('/stories'),
  getById: (id) => api.get(`/stories/${id}`),
  create: (data) => api.post('/stories', data),
  update: (id, data) => api.put(`/stories/${id}`, data),
  delete: (id) => api.delete(`/stories/${id}`),
  linkEntities: (id, data) => api.post(`/stories/${id}/link-entities`, data),
  clearLinks: (id) => api.post(`/stories/${id}/clear-links`),
}

// GPT API
export const gptAPI = {
  analyze: (data) => api.post('/gpt/analyze', data),
  generateDescription: (data) => api.post('/gpt/generate-description', data),
  getResults: (taskId) => api.get(`/gpt/results/${taskId}`),
  batchAnalyzeStories: (data) => api.post('/gpt/batch-analyze-stories', data),
}

// Stats API
export const statsAPI = {
  get: () => api.get('/stats'),
}

// Visualization API
export const visualizationAPI = {
  getRelationshipDiagram: (worldId) => api.get(`/worlds/${worldId}/relationships`),
}

// Events / Timeline API
export const eventsAPI = {
  getWorldTimeline: (worldId) => api.get(`/worlds/${worldId}/events`),
  extractFromWorld: (worldId, force = false) =>
    api.post(`/worlds/${worldId}/events/extract${force ? '?force=true' : ''}`),
  extractFromStory: (storyId, force = false) =>
    api.post(`/stories/${storyId}/events/extract${force ? '?force=true' : ''}`),
  updateEvent: (eventId, data) => api.put(`/events/${eventId}`, data),
  deleteEvent: (eventId) => api.delete(`/events/${eventId}`),
  addConnection: (eventId, data) => api.post(`/events/${eventId}/connections`, data),
  clearStoryCache: (storyId) => api.delete(`/stories/${storyId}/events/cache`),
}

// Authentication API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  verify: () => api.get('/auth/verify'),
  changePassword: (data) => api.post('/auth/change-password', data),
  getCurrentUser: () => api.get('/auth/me'),
  // OAuth
  googleLogin: (token) => api.post('/auth/oauth/google', { token }),
  facebookLogin: (token) => api.post('/auth/oauth/facebook', { token }),
}

// Admin API
export const adminAPI = {
  // User management
  getAllUsers: (params) => api.get('/admin/users', { params }),
  getUserDetail: (userId) => api.get(`/admin/users/${userId}`),
  changeUserRole: (userId, role) => api.put(`/admin/users/${userId}/role`, { role }),
  banUser: (userId, banned, reason) => api.post(`/admin/users/${userId}/ban`, { banned, reason }),

  // System info
  getRoles: () => api.get('/admin/roles'),
  getAdminStats: () => api.get('/admin/stats')
}

export default api
