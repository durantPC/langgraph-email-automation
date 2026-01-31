import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 用户状态
export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  
  const isLoggedIn = computed(() => !!token.value)
  
  function setUser(newToken, newUsername) {
    token.value = newToken
    username.value = newUsername
    localStorage.setItem('token', newToken)
    localStorage.setItem('username', newUsername)
  }
  
  function logout() {
    token.value = ''
    username.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
  }
  
  return {
    token,
    username,
    isLoggedIn,
    setUser,
    logout
  }
})

// 系统状态
export const useSystemStore = defineStore('system', () => {
  const isRunning = ref(false)
  const lastCheckTime = ref(null)
  const emailCount = ref(0)
  const pendingCount = ref(0)
  
  function setStatus(status) {
    isRunning.value = status.running
    lastCheckTime.value = status.lastCheckTime
    emailCount.value = status.emailCount
    pendingCount.value = status.pendingCount
  }
  
  function start() {
    isRunning.value = true
    lastCheckTime.value = new Date().toISOString()
  }
  
  function stop() {
    isRunning.value = false
  }
  
  return {
    isRunning,
    lastCheckTime,
    emailCount,
    pendingCount,
    setStatus,
    start,
    stop
  }
})

