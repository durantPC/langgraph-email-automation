<template>
  <router-view />
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { initTheme } from '@/utils/theme'
import { requestNotificationPermission } from '@/utils/notification'
import api from '@/api'

const route = useRoute()

// 从后端获取用户偏好设置并应用
const loadUserPreferences = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    // 未登录时使用默认主题
    initTheme()
    return
  }
  
  const username = localStorage.getItem('username') || 'admin'
  
  try {
    // 从后端获取最新偏好设置
    const preferencesRes = await api.get('/auth/preferences')
    if (preferencesRes) {
      // 保存到localStorage
      localStorage.setItem(`userPreferences-${username}`, JSON.stringify(preferencesRes))
      
      // 应用主题
      if (preferencesRes.theme) {
        const { applyTheme } = await import('@/utils/theme')
        applyTheme(preferencesRes.theme)
      }
      
      // 请求通知权限
      if (preferencesRes.notification) {
        requestNotificationPermission()
      }
    }
  } catch (e) {
    console.warn('获取用户偏好设置失败，使用localStorage中的设置', e)
    // 如果获取失败，使用localStorage中的设置
    initTheme()
    
    // 请求通知权限（如果localStorage中有设置）
    const savedPreferences = localStorage.getItem(`userPreferences-${username}`)
    if (savedPreferences) {
      try {
        const preferences = JSON.parse(savedPreferences)
        if (preferences.notification) {
          requestNotificationPermission()
        }
      } catch (parseError) {
        console.error('解析用户偏好设置失败', parseError)
      }
    }
  }
}

onMounted(() => {
  // 初始化主题（优先从后端获取）
  loadUserPreferences()
})

// 监听路由变化，当用户登录后跳转时重新加载偏好设置
watch(() => route.path, (newPath, oldPath) => {
  const token = localStorage.getItem('token')
  // 如果从登录/注册页跳转到需要认证的页面，重新加载偏好设置
  if (token && (oldPath === '/login' || oldPath === '/register') && newPath !== '/login' && newPath !== '/register') {
    loadUserPreferences()
  }
})
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
</style>

