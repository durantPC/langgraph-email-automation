/**
 * 主题管理工具
 */

/**
 * 应用主题
 * @param {string} theme - 主题类型: 'light' | 'dark' | 'auto'
 */
export function applyTheme(theme) {
  const html = document.documentElement
  
  // 移除所有主题类
  html.classList.remove('theme-light', 'theme-dark')
  
  if (theme === 'auto') {
    // 跟随系统
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    html.classList.add(prefersDark ? 'theme-dark' : 'theme-light')
    
    // 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e) => {
      html.classList.remove('theme-light', 'theme-dark')
      html.classList.add(e.matches ? 'theme-dark' : 'theme-light')
    }
    
    // 移除旧的监听器（如果存在）
    if (window.themeMediaQueryListener) {
      mediaQuery.removeEventListener('change', window.themeMediaQueryListener)
    }
    
    // 添加新的监听器
    window.themeMediaQueryListener = handleChange
    mediaQuery.addEventListener('change', handleChange)
  } else {
    // 固定主题
    html.classList.add(theme === 'dark' ? 'theme-dark' : 'theme-light')
    
    // 移除系统主题监听器
    if (window.themeMediaQueryListener) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.removeEventListener('change', window.themeMediaQueryListener)
      window.themeMediaQueryListener = null
    }
  }
  
  // 保存到localStorage
  localStorage.setItem('theme', theme)
}

/**
 * 初始化主题（从localStorage或用户偏好设置加载）
 */
export function initTheme() {
  // 优先从用户偏好设置加载
  const username = localStorage.getItem('username') || 'admin'
  const savedPreferences = localStorage.getItem(`userPreferences-${username}`)
  
  let theme = 'light'
  
  if (savedPreferences) {
    try {
      const preferences = JSON.parse(savedPreferences)
      theme = preferences.theme || 'light'
    } catch (e) {
      console.error('解析用户偏好设置失败', e)
    }
  } else {
    // 如果没有用户偏好设置，从localStorage加载
    theme = localStorage.getItem('theme') || 'light'
  }
  
  applyTheme(theme)
  return theme
}

