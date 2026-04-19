import axios from 'axios'

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === 'production' ? '/api' : '/api')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach auth token to every request. Guard localStorage so SSR (server-side
// axios calls during Next.js render) doesn't throw "localStorage is not defined".
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const authToken = localStorage.getItem('auth_token')
      if (authToken) {
        config.headers.Authorization = `Bearer ${authToken}`
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Unwrap standard API response envelope: { success: true, data: X } → response.data = X
// GPT endpoints use jsonify() directly (no envelope) so they are unaffected.
// Pagination metadata (if present) is preserved on response.pagination.
api.interceptors.response.use(
  (response) => {
    if (
      response.data &&
      typeof response.data === 'object' &&
      'success' in response.data &&
      'data' in response.data
    ) {
      if (response.data.pagination) {
        response.pagination = response.data.pagination
      }
      response.data = response.data.data
    }
    return response
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
  getStories: (id, { page = 1, perPage = 20 } = {}) =>
    api.get(`/worlds/${id}/stories`, { params: { page, per_page: perPage } }),
  getLocations: (id) => api.get(`/worlds/${id}/locations`),
  autoLinkStories: (id) => api.post(`/worlds/${id}/auto-link-stories`),
  deleteEntity: (worldId, entityId) => api.delete(`/worlds/${worldId}/entities/${entityId}`),
  updateEntity: (worldId, entityId, data) => api.put(`/worlds/${worldId}/entities/${entityId}`, data),
  deleteLocation: (worldId, locationId) => api.delete(`/worlds/${worldId}/locations/${locationId}`),
  updateLocation: (worldId, locationId, data) => api.put(`/worlds/${worldId}/locations/${locationId}`, data),
}

// Stories API
export const storiesAPI = {
  getAll: () => api.get('/stories'),
  getById: (id) => api.get(`/stories/${id}`),
  create: (data) => api.post('/stories', data),
  update: (id, data) => api.put(`/stories/${id}`, data),
  patch: (id, data) => api.patch(`/stories/${id}`, data),
  delete: (id) => api.delete(`/stories/${id}`),
  linkEntities: (id, data) => api.post(`/stories/${id}/link-entities`, data),
  clearLinks: (id) => api.post(`/stories/${id}/clear-links`),
  getMyDraft: () => api.get('/stories/my-draft'),
  getNeighbors: (id) => api.get(`/stories/${id}/neighbors`),
}

// GPT API
export const gptAPI = {
  analyze: (data) => api.post('/gpt/analyze', data),
  generateDescription: (data) => api.post('/gpt/generate-description', data),
  getResults: (taskId) => api.get(`/gpt/results/${taskId}`),
  batchAnalyzeStories: (data) => api.post('/gpt/batch-analyze-stories', data),
  getTasks: (taskIds) => api.get('/gpt/tasks', { params: { task_ids: taskIds.join(',') } }),
  paraphrase: (text, mode) => api.post('/gpt/paraphrase', { text, mode }),
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
  updateProfile: (data) => api.put('/auth/profile', data),
  // OAuth
  googleLogin: (token) => api.post('/auth/oauth/google', { token }),
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

// Collaborators API
export const collaboratorsAPI = {
  list:   (worldId)            => api.get(`/worlds/${worldId}/collaborators`),
  invite: (worldId, usernameOrEmail) => api.post(`/worlds/${worldId}/collaborators`, { username_or_email: usernameOrEmail, role: 'co_author' }),
  remove: (worldId, userId)    => api.delete(`/worlds/${worldId}/collaborators/${userId}`),
}

// Novel API
export const novelAPI = {
  get:             (worldId)        => api.get(`/worlds/${worldId}/novel`),
  update:          (worldId, data)  => api.put(`/worlds/${worldId}/novel`, data),
  reorderChapters: (worldId, order) => api.patch(`/worlds/${worldId}/novel/chapters`, { order }),
  getContent:      (worldId, { cursor, lineBudget } = {}) => {
    const params = {}
    if (cursor) params.cursor = cursor
    if (lineBudget) params.line_budget = lineBudget
    return api.get(`/worlds/${worldId}/novel/content`, { params })
  },
}

// Invitations API
export const invitationsAPI = {
  list:    ()    => api.get('/users/me/invitations'),
  accept:  (id)  => api.post(`/users/me/invitations/${id}/accept`),
  decline: (id)  => api.post(`/users/me/invitations/${id}/decline`),
}
