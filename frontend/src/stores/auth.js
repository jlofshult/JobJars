import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getMe } from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('jobjars_token') || null)

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isParent = computed(() => user.value?.role === 'parent')
  const isChild = computed(() => user.value?.role === 'child')

  async function login(username, password) {
    const response = await apiLogin(username, password)
    const data = response.data
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('jobjars_token', data.access_token)
    localStorage.setItem('jobjars_user', JSON.stringify(data.user))
    return data
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('jobjars_token')
    localStorage.removeItem('jobjars_user')
  }

  async function loadUser() {
    const savedToken = localStorage.getItem('jobjars_token')
    if (!savedToken) {
      return false
    }
    token.value = savedToken
    const savedUser = localStorage.getItem('jobjars_user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch {
        user.value = null
      }
    }
    try {
      const response = await getMe()
      user.value = response.data
      localStorage.setItem('jobjars_user', JSON.stringify(response.data))
      return true
    } catch {
      logout()
      return false
    }
  }

  return { user, token, isLoggedIn, isParent, isChild, login, logout, loadUser }
})
