import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
}

// Stats API
export const statsAPI = {
  get: () => api.get('/stats'),
}

// Visualization API
export const visualizationAPI = {
  getRelationshipDiagram: (worldId) => api.get(`/worlds/${worldId}/relationships`),
}

export default api
