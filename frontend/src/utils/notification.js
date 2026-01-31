/**
 * 消息通知工具
 */

let notificationPermission = null

/**
 * 请求通知权限
 */
export async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.warn('此浏览器不支持桌面通知')
    return false
  }
  
  if (Notification.permission === 'granted') {
    return true
  }
  
  if (Notification.permission === 'denied') {
    console.warn('用户已拒绝通知权限')
    return false
  }
  
  // 请求权限
  const permission = await Notification.requestPermission()
  notificationPermission = permission === 'granted'
  return notificationPermission
}

/**
 * 显示桌面通知
 * @param {string} title - 通知标题
 * @param {object} options - 通知选项
 */
export function showNotification(title, options = {}) {
  // 检查是否启用通知
  const username = localStorage.getItem('username') || 'admin'
  const savedPreferences = localStorage.getItem(`userPreferences-${username}`)
  
  if (savedPreferences) {
    try {
      const preferences = JSON.parse(savedPreferences)
      if (!preferences.notification) {
        return // 用户未启用通知
      }
    } catch (e) {
      console.error('解析用户偏好设置失败', e)
    }
  }
  
  if (!('Notification' in window)) {
    console.warn('此浏览器不支持桌面通知')
    return
  }
  
  if (Notification.permission !== 'granted') {
    // 尝试请求权限
    requestNotificationPermission().then(granted => {
      if (granted) {
        new Notification(title, {
          icon: '/favicon.ico',
          badge: '/favicon.ico',
          ...options
        })
      }
    })
    return
  }
  
  // 显示通知
  new Notification(title, {
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    ...options
  })
}

/**
 * 显示新邮件通知
 * @param {string} sender - 发件人
 * @param {string} subject - 邮件主题
 */
export function showEmailNotification(sender, subject) {
  showNotification('新邮件到达', {
    body: `来自 ${sender}: ${subject}`,
    tag: 'email-notification',
    requireInteraction: false
  })
}

/**
 * 显示处理完成通知
 * @param {string} message - 消息内容
 */
export function showProcessCompleteNotification(message) {
  showNotification('处理完成', {
    body: message,
    tag: 'process-complete',
    requireInteraction: false
  })
}

