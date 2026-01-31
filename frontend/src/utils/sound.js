/**
 * 声音提醒工具
 */

let audioContext = null
let soundEnabled = true

/**
 * 初始化音频上下文
 */
function initAudioContext() {
  if (!audioContext && typeof AudioContext !== 'undefined') {
    audioContext = new (window.AudioContext || window.webkitAudioContext)()
  }
}

/**
 * 播放提示音
 * @param {string} type - 声音类型: 'success' | 'error' | 'info'
 */
export function playSound(type = 'success') {
  // 检查是否启用声音
  const username = localStorage.getItem('username') || 'admin'
  const savedPreferences = localStorage.getItem(`userPreferences-${username}`)
  
  if (savedPreferences) {
    try {
      const preferences = JSON.parse(savedPreferences)
      if (!preferences.sound) {
        return // 用户未启用声音
      }
    } catch (e) {
      console.error('解析用户偏好设置失败', e)
    }
  }
  
  initAudioContext()
  
  if (!audioContext) {
    console.warn('浏览器不支持Web Audio API')
    return
  }
  
  // 创建简单的提示音
  const oscillator = audioContext.createOscillator()
  const gainNode = audioContext.createGain()
  
  oscillator.connect(gainNode)
  gainNode.connect(audioContext.destination)
  
  // 根据类型设置频率
  switch (type) {
    case 'success':
      oscillator.frequency.value = 800
      break
    case 'error':
      oscillator.frequency.value = 400
      break
    case 'info':
      oscillator.frequency.value = 600
      break
    default:
      oscillator.frequency.value = 600
  }
  
  // 设置音量
  gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
  
  // 播放
  oscillator.start(audioContext.currentTime)
  oscillator.stop(audioContext.currentTime + 0.3)
}

/**
 * 播放成功提示音
 */
export function playSuccessSound() {
  playSound('success')
}

/**
 * 播放错误提示音
 */
export function playErrorSound() {
  playSound('error')
}

/**
 * 播放信息提示音
 */
export function playInfoSound() {
  playSound('info')
}

