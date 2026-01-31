import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' }
      },
      {
        path: 'emails',
        name: 'Emails',
        component: () => import('@/views/Emails.vue'),
        meta: { title: '邮件管理', icon: 'Message' }
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/History.vue'),
        meta: { title: '处理记录', icon: 'Document' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/views/Knowledge.vue'),
        meta: { title: '知识库', icon: 'Collection' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', icon: 'User' }
      },
      {
        path: 'ai-assistant',
        name: 'AiAssistant',
        component: () => import('@/views/AiAssistant.vue'),
        meta: { title: 'AI助教', icon: 'Service' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 邮件自动化系统` : '邮件自动化系统'
  
  const token = localStorage.getItem('token')
  
  // 如果用户已登录且从登录/注册页跳转，立即加载用户偏好设置并应用主题
  if (token && (from.path === '/login' || from.path === '/register') && to.meta.requiresAuth) {
    try {
      const { initTheme } = await import('@/utils/theme')
      // 重新初始化主题（从后端获取最新偏好设置）
      const username = localStorage.getItem('username') || 'admin'
      const api = (await import('@/api')).default
      
      try {
        const preferencesRes = await api.get('/auth/preferences')
        if (preferencesRes) {
          localStorage.setItem(`userPreferences-${username}`, JSON.stringify(preferencesRes))
          const { applyTheme } = await import('@/utils/theme')
          if (preferencesRes.theme) {
            applyTheme(preferencesRes.theme)
          }
        }
      } catch (prefError) {
        // 如果获取失败，使用localStorage中的设置
        initTheme()
      }
    } catch (e) {
      console.warn('初始化主题失败', e)
    }
  }
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && token) {
    // 登录后跳转到用户设置的默认页面
    // 优先从后端获取最新设置
    try {
      const api = (await import('@/api')).default
      const preferencesRes = await api.get('/auth/preferences')
      if (preferencesRes && preferencesRes.defaultPage) {
        next(preferencesRes.defaultPage)
        return
      }
    } catch (e) {
      console.warn('从后端获取默认页面失败，使用localStorage', e)
    }
    
    // 如果后端获取失败，从localStorage读取
    const username = localStorage.getItem('username') || 'admin'
    const savedPreferences = localStorage.getItem(`userPreferences-${username}`)
    let defaultPage = '/dashboard'
    
    if (savedPreferences) {
      try {
        const preferences = JSON.parse(savedPreferences)
        if (preferences.defaultPage) {
          defaultPage = preferences.defaultPage
        }
      } catch (e) {
        console.error('解析用户偏好设置失败', e)
      }
    }
    
    next(defaultPage)
  } else if (to.path === '/' && token) {
    // 根路径也跳转到默认页面
    // 优先从后端获取最新设置
    try {
      const api = (await import('@/api')).default
      const preferencesRes = await api.get('/auth/preferences')
      if (preferencesRes && preferencesRes.defaultPage) {
        next(preferencesRes.defaultPage)
        return
      }
    } catch (e) {
      console.warn('从后端获取默认页面失败，使用localStorage', e)
    }
    
    // 如果后端获取失败，从localStorage读取
    const username = localStorage.getItem('username') || 'admin'
    const savedPreferences = localStorage.getItem(`userPreferences-${username}`)
    let defaultPage = '/dashboard'
    
    if (savedPreferences) {
      try {
        const preferences = JSON.parse(savedPreferences)
        if (preferences.defaultPage) {
          defaultPage = preferences.defaultPage
        }
      } catch (e) {
        console.error('解析用户偏好设置失败', e)
      }
    }
    
    next(defaultPage)
  } else {
    next()
  }
})

export default router

