/**
 * AI助教 API 接口
 * 统一封装AI聊天接口，支持真实后端和Mock模式
 */
import api from './index'

// 是否使用Mock模式（开发环境且后端未实现时使用）
const USE_MOCK = false

// Mock响应延迟（毫秒）
const MOCK_DELAY = 800

// Mock回复数据库
const MOCK_RESPONSES = {
  '如何接入邮箱账号': `要接入邮箱账号，请按以下步骤操作：

1. **进入系统设置**
   点击左侧菜单的"系统设置"进入配置页面。

2. **配置QQ邮箱**
   - 邮箱地址：填写您的QQ邮箱完整地址（如：xxx@qq.com）
   - 授权码：填写QQ邮箱的授权码（非登录密码）

3. **获取授权码**
   - 登录QQ邮箱网页版
   - 进入"设置" → "账户"
   - 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
   - 开启"IMAP/SMTP服务"
   - 按提示获取16位授权码

4. **测试连接**
   配置完成后点击"测试连接"验证配置是否正确。`,

  '如何配置邮件处理规则': `邮件处理规则配置说明：

1. **自动处理模式**
   在"系统设置"中开启"自动处理"开关，系统会自动处理收到的邮件。

2. **邮件分类**
   系统会自动将邮件分为以下类别：
   - 产品咨询：关于产品功能、价格等的咨询
   - 客户投诉：客户的投诉和不满
   - 客户反馈：客户的建议和意见
   - 无关邮件：广告、垃圾邮件等

3. **知识库配置**
   在"知识库"页面上传相关文档，AI会基于这些知识生成更精准的回复。

4. **监控间隔**
   在"系统设置"中可以配置邮件检查间隔（默认15分钟）。`,

  '处理失败怎么排查': `邮件处理失败排查指南：

1. **检查API配置**
   - 确认硅基流动API密钥是否正确
   - 在"系统设置"中点击"测试AI连接"验证

2. **检查邮箱连接**
   - 确认邮箱地址和授权码正确
   - 点击"测试邮箱连接"验证

3. **查看错误日志**
   - 检查浏览器控制台是否有错误信息
   - 查看后端终端输出的错误日志

4. **常见问题**
   - API额度不足：检查硅基流动账户余额
   - 网络问题：确认能正常访问API服务
   - 邮件过大：部分邮件内容过长可能导致处理超时

5. **重试处理**
   在"邮件管理"页面找到失败的邮件，点击"重新处理"。`,

  '知识库如何使用': `知识库使用指南：

1. **上传文档**
   - 进入"知识库"页面
   - 点击"上传文档"按钮
   - 支持 TXT、MD、PDF 等格式

2. **文档管理**
   - 查看已上传的文档列表
   - 可以预览、下载或删除文档

3. **重建索引**
   - 上传新文档后点击"重建索引"
   - 系统会自动将文档内容向量化

4. **RAG测试**
   - 在知识库页面可以测试问答效果
   - 输入问题查看AI基于知识库的回答

5. **最佳实践**
   - 上传产品手册、FAQ等文档
   - 保持文档内容清晰、结构化
   - 定期更新知识库内容`
}

/**
 * 生成Mock回复
 * @param {string} message 用户消息
 * @returns {string} Mock回复内容
 */
const generateMockResponse = (message) => {
  // 检查是否匹配预设问题
  for (const [key, response] of Object.entries(MOCK_RESPONSES)) {
    if (message.includes(key) || key.includes(message)) {
      return response
    }
  }
  
  // 通用回复
  return `感谢您的提问！

关于"${message}"，我可以为您提供以下帮助：

1. **系统使用**：您可以通过左侧菜单访问各个功能模块
2. **邮件处理**：在"邮件管理"页面可以手动或自动处理邮件
3. **配置设置**：在"系统设置"中可以配置邮箱和AI模型
4. **知识库**：上传相关文档让AI回复更精准

如果您有更具体的问题，请详细描述，我会尽力帮助您！

💡 提示：您也可以点击快捷问题按钮快速获取常见问题的答案。`
}

/**
 * AI助教API
 */
export const aiAssistantApi = {
  /**
   * 发送聊天消息
   * @param {Object} params 请求参数
   * @param {string|null} params.conversationId 会话ID
   * @param {string} params.message 用户消息
   * @param {Object} params.pageContext 页面上下文
   * @returns {Promise<Object>} 响应数据
   */
  chat: async ({ conversationId, message, pageContext }) => {
    if (USE_MOCK) {
      // Mock模式
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            conversationId: conversationId || `conv_${Date.now()}`,
            answer: generateMockResponse(message),
            sources: []
          })
        }, MOCK_DELAY)
      })
    }
    
    // 真实API调用
    try {
      const response = await api.post('/ai/chat', {
        conversationId,
        message,
        pageContext
      })
      return response
    } catch (error) {
      // 如果后端接口不存在（404），使用Mock
      if (error.response?.status === 404) {
        console.warn('[AI助教] 后端接口不存在，使用Mock模式')
        return {
          conversationId: conversationId || `conv_${Date.now()}`,
          answer: generateMockResponse(message),
          sources: []
        }
      }
      throw error
    }
  },

  /**
   * 获取会话历史
   * @param {string} conversationId 会话ID
   * @returns {Promise<Object>} 会话历史
   */
  getHistory: async (conversationId) => {
    if (USE_MOCK) {
      return { messages: [] }
    }
    
    try {
      return await api.get(`/ai/history/${conversationId}`)
    } catch (error) {
      if (error.response?.status === 404) {
        return { messages: [] }
      }
      throw error
    }
  },

  /**
   * 清除会话历史
   * @param {string} conversationId 会话ID
   * @returns {Promise<void>}
   */
  clearHistory: async (conversationId) => {
    if (USE_MOCK) {
      return { success: true }
    }
    
    try {
      return await api.delete(`/ai/history/${conversationId}`)
    } catch (error) {
      if (error.response?.status === 404) {
        return { success: true }
      }
      throw error
    }
  },

  // ==================== 聊天记录持久化 API ====================

  /**
   * 保存当前会话到历史记录
   * @param {Object} params 参数
   * @param {string} params.conversationId 会话ID
   * @param {Array} params.messages 消息列表
   * @param {string} params.title 会话标题（可选）
   * @returns {Promise<Object>}
   */
  saveConversation: async ({ conversationId, messages, title }) => {
    try {
      return await api.post('/ai/conversations/save', {
        conversationId,
        messages,
        title
      })
    } catch (error) {
      console.error('[AI助教] 保存会话失败:', error)
      throw error
    }
  },

  /**
   * 获取所有聊天记录列表
   * @returns {Promise<Object>}
   */
  getConversations: async () => {
    try {
      return await api.get('/ai/conversations')
    } catch (error) {
      console.error('[AI助教] 获取聊天记录列表失败:', error)
      return { success: true, conversations: [] }
    }
  },

  /**
   * 获取单个聊天记录详情
   * @param {string} conversationId 会话ID
   * @returns {Promise<Object>}
   */
  getConversationDetail: async (conversationId) => {
    try {
      return await api.get(`/ai/conversations/${conversationId}`)
    } catch (error) {
      console.error('[AI助教] 获取聊天记录详情失败:', error)
      throw error
    }
  },

  /**
   * 删除单个聊天记录
   * @param {string} conversationId 会话ID
   * @returns {Promise<Object>}
   */
  deleteConversation: async (conversationId) => {
    try {
      return await api.delete(`/ai/conversations/${conversationId}`)
    } catch (error) {
      console.error('[AI助教] 删除聊天记录失败:', error)
      throw error
    }
  },

  /**
   * 清空所有聊天记录
   * @returns {Promise<Object>}
   */
  clearAllConversations: async () => {
    try {
      return await api.delete('/ai/conversations')
    } catch (error) {
      console.error('[AI助教] 清空聊天记录失败:', error)
      throw error
    }
  }
}

export default aiAssistantApi

