import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jobjars_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('jobjars_token')
      localStorage.removeItem('jobjars_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth
export function login(username, password) {
  return api.post('/auth/login', { username, password })
}

export function getMe() {
  return api.get('/auth/me')
}

// Users / Children
export function getChildren() {
  return api.get('/users/children')
}

export function createChild(data) {
  return api.post('/users/children', data)
}

export function updateChild(id, data) {
  return api.put(`/users/children/${id}`, data)
}

export function deleteChild(id) {
  return api.delete(`/users/children/${id}`)
}

// Chores
export function getChores() {
  return api.get('/chores')
}

export function createChore(data) {
  return api.post('/chores', data)
}

export function updateChore(id, data) {
  return api.put(`/chores/${id}`, data)
}

export function deleteChore(id) {
  return api.delete(`/chores/${id}`)
}

export function getAssignments() {
  return api.get('/chores/assignments')
}

export function claimChore(choreId) {
  return api.post(`/chores/${choreId}/claim`)
}

export function completeAssignment(id) {
  return api.put(`/chores/assignments/${id}/complete`)
}

export function approveAssignment(id) {
  return api.put(`/chores/assignments/${id}/approve`)
}

export function rejectAssignment(id, reason) {
  return api.put(`/chores/assignments/${id}/reject`, { reason })
}

// Rewards
export function getBalance() {
  return api.get('/rewards/balance')
}

export function getRedemptions() {
  return api.get('/rewards/redemptions')
}

export function requestRedemption(amount, description) {
  return api.post('/rewards/redeem', { amount, description })
}

export function approveRedemption(id) {
  return api.put(`/rewards/redemptions/${id}/approve`)
}

export function rejectRedemption(id) {
  return api.put(`/rewards/redemptions/${id}/reject`)
}

export default api
