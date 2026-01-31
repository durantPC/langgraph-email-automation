/**
 * AI助教状态管理
 * 管理聊天消息、会话状态，供页面和弹窗共享
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { aiAssistantApi } from '@/api/aiAssistant'

// localStorage keys
const STORAGE_KEYS = {
  BOT_HIDDEN: 'ai_bot_hidden_v1',
  BOT_POSITION: 'ai_bot_pos_v1',
  CONVERSATION_ID: 'ai_conversation_id_v1',
  MESSAGES: 'ai_messages_v1'
}

/**
 * AI助教 Store
 */
export const useAiAssistantStore = defineStore('aiAssistant', () => {
  // ========== 状态 ==========
  
  /** 消息列表 */
  const messages = ref([])
  
  /** 当前会话ID */
  const conversationId = ref(null)
  
  /** 是否正在加载（发送消息中） */
  const loading = ref(false)
  
  /** 错误信息 */
  const error = ref(null)
  
  /** 弹窗是否打开 */
  const modalVisible = ref(false)
  
  /** 悬浮机器人是否隐藏 */
  const botHidden = ref(false)
  
  /** 悬浮机器人位置 */
  const botPosition = ref({ x: null, y: null })

  // ========== 计算属性 ==========
  
  /** 是否有消息 */
  const hasMessages = computed(() => messages.value.length > 0)
  
  /** 最后一条消息 */
  const lastMessage = computed(() => {
    if (messages.value.length === 0) return null
    return messages.value[messages.value.length - 1]
  })

  // ========== 初始化 ==========
  
  /**
   * 从localStorage加载状态
   */
  const loadFromStorage = () => {
    try {
      // 加载机器人隐藏状态
      const hidden = localStorage.getItem(STORAGE_KEYS.BOT_HIDDEN)
      botHidden.value = hidden === '1'
      
      // 加载机器人位置
      const posStr = localStorage.getItem(STORAGE_KEYS.BOT_POSITION)
      if (posStr) {
        const pos = JSON.parse(posStr)
        if (pos && typeof pos.x === 'number' && typeof pos.y === 'number') {
          botPosition.value = pos
        }
      }
      
      // 加载会话ID
      const savedConvId = localStorage.getItem(STORAGE_KEYS.CONVERSATION_ID)
      if (savedConvId) {
        conversationId.value = savedConvId
      }
      
      // 加载消息历史
      const savedMessages = localStorage.getItem(STORAGE_KEYS.MESSAGES)
      if (savedMessages) {
        messages.value = JSON.parse(savedMessages)
      }
    } catch (e) {
      console.error('[AI助教] 加载本地存储失败:', e)
    }
  }
  
  /**
   * 保存消息到localStorage
   */
  const saveMessagesToStorage = () => {
    try {
      localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(messages.value))
      if (conversationId.value) {
        localStorage.setItem(STORAGE_KEYS.CONVERSATION_ID, conversationId.value)
      }
    } catch (e) {
      console.error('[AI助教] 保存消息失败:', e)
    }
  }

  // ========== 方法 ==========
  
  /**
   * 发送消息
   * @param {string} content 消息内容
   * @param {Object} pageContext 页面上下文
   * @returns {Promise<void>}
   */
  const sendMessage = async (content, pageContext = {}) => {
    if (!content.trim() || loading.value) return
    
    // 添加用户消息
    const userMessage = {
      id: `msg_${Date.now()}_user`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString()
    }
    messages.value.push(userMessage)
    
    // 开始加载
    loading.value = true
    error.value = null
    
    try {
      // 调用API
      const response = await aiAssistantApi.chat({
        conversationId: conversationId.value,
        message: content.trim(),
        pageContext
      })
      
      // 更新会话ID
      if (response.conversationId) {
        conversationId.value = response.conversationId
      }
      
      // 添加助手消息
      const assistantMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        timestamp: new Date().toISOString()
      }
      messages.value.push(assistantMessage)
      
      // 保存到localStorage
      saveMessagesToStorage()
    } catch (e) {
      console.error('[AI助教] 发送消息失败:', e)
      error.value = e.message || '发送失败，请稍后重试'
      
      // 添加错误消息
      const errorMessage = {
        id: `msg_${Date.now()}_error`,
        role: 'assistant',
        content: '抱歉，处理您的问题时遇到了错误。请稍后重试。',
        isError: true,
        timestamp: new Date().toISOString()
      }
      messages.value.push(errorMessage)
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 保存当前会话到历史记录
   * @returns {Promise<boolean>} 是否保存成功
   */
  const saveCurrentConversation = async () => {
    if (messages.value.length === 0 || !conversationId.value) {
      return false
    }
    
    try {
      await aiAssistantApi.saveConversation({
        conversationId: conversationId.value,
        messages: messages.value
      })
      console.log('[AI助教] 会话已保存到历史记录')
      return true
    } catch (e) {
      console.error('[AI助教] 保存会话失败:', e)
      return false
    }
  }
  
  /**
   * 清空会话（新建会话）
   * 会先保存当前会话到历史记录
   */
  const clearConversation = async () => {
    // 先保存当前会话
    if (messages.value.length > 0) {
      await saveCurrentConversation()
    }
    
    // 清空当前会话
    messages.value = []
    conversationId.value = null
    error.value = null
    
    // 清除localStorage
    localStorage.removeItem(STORAGE_KEYS.MESSAGES)
    localStorage.removeItem(STORAGE_KEYS.CONVERSATION_ID)
  }
  
  /**
   * 获取聊天记录列表
   * @returns {Promise<Array>}
   */
  const getConversationsList = async () => {
    try {
      const response = await aiAssistantApi.getConversations()
      return response.conversations || []
    } catch (e) {
      console.error('[AI助教] 获取聊天记录失败:', e)
      return []
    }
  }
  
  /**
   * 获取聊天记录详情
   * @param {string} convId 会话ID
   * @returns {Promise<Object|null>}
   */
  const getConversationDetail = async (convId) => {
    try {
      const response = await aiAssistantApi.getConversationDetail(convId)
      return response.conversation || null
    } catch (e) {
      console.error('[AI助教] 获取聊天记录详情失败:', e)
      return null
    }
  }
  
  /**
   * 删除聊天记录
   * @param {string} convId 会话ID
   * @returns {Promise<boolean>}
   */
  const deleteConversation = async (convId) => {
    try {
      await aiAssistantApi.deleteConversation(convId)
      return true
    } catch (e) {
      console.error('[AI助教] 删除聊天记录失败:', e)
      return false
    }
  }
  
  /**
   * 清空所有聊天记录
   * @returns {Promise<boolean>}
   */
  const clearAllConversations = async () => {
    try {
      await aiAssistantApi.clearAllConversations()
      return true
    } catch (e) {
      console.error('[AI助教] 清空聊天记录失败:', e)
      return false
    }
  }
  
  /**
   * 打开弹窗
   */
  const openModal = () => {
    modalVisible.value = true
  }
  
  /**
   * 关闭弹窗
   */
  const closeModal = () => {
    modalVisible.value = false
  }
  
  /**
   * 打开弹窗并发送消息
   * @param {string} message 要发送的消息
   * @param {Object} pageContext 页面上下文
   */
  const openModalWithMessage = async (message, pageContext = {}) => {
    openModal()
    // 等待弹窗打开动画
    await new Promise(resolve => setTimeout(resolve, 100))
    await sendMessage(message, pageContext)
  }
  
  /**
   * 设置机器人隐藏状态
   * @param {boolean} hidden 是否隐藏
   */
  const setBotHidden = (hidden) => {
    botHidden.value = hidden
    if (hidden) {
      localStorage.setItem(STORAGE_KEYS.BOT_HIDDEN, '1')
    } else {
      localStorage.removeItem(STORAGE_KEYS.BOT_HIDDEN)
    }
  }
  
  /**
   * 设置机器人位置
   * @param {Object} position 位置 {x, y}
   */
  const setBotPosition = (position) => {
    botPosition.value = position
    localStorage.setItem(STORAGE_KEYS.BOT_POSITION, JSON.stringify(position))
  }
  
  /**
   * 恢复显示机器人
   */
  const showBot = () => {
    setBotHidden(false)
  }
  
  /**
   * 隐藏机器人
   */
  const hideBot = () => {
    setBotHidden(true)
  }

  // 初始化时加载存储
  loadFromStorage()

  return {
    // 状态
    messages,
    conversationId,
    loading,
    error,
    modalVisible,
    botHidden,
    botPosition,
    
    // 计算属性
    hasMessages,
    lastMessage,
    
    // 方法
    sendMessage,
    clearConversation,
    saveCurrentConversation,
    getConversationsList,
    getConversationDetail,
    deleteConversation,
    clearAllConversations,
    openModal,
    closeModal,
    openModalWithMessage,
    setBotHidden,
    setBotPosition,
    showBot,
    hideBot,
    loadFromStorage
  }
})

export default useAiAssistantStore

