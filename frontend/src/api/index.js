import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',  // 直接指向后端API
  timeout: 300000,  // 5分钟
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 先检查是否是取消请求（AbortError）
    if (error.name === 'AbortError' || error.message === 'canceled' || error.code === 'ERR_CANCELED' || error.code === 'ERR_ABORTED') {
      // 取消请求时不显示错误消息，让调用方自己处理
      // 设置一个标记，方便调用方识别
      error.isCanceled = true
      return Promise.reject(error)
    }
    
    if (error.response) {
      // FastAPI 的错误信息在 detail 字段中
      const errorDetail = error.response.data?.detail || error.response.data?.message || '请求失败'
      
      switch (error.response.status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          router.push('/login')
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 400:
          // 400 错误不在这里统一处理，让调用方自己处理（可以显示更友好的提示）
          // 只在控制台记录，不显示通用错误消息
          console.warn('请求失败 (400):', errorDetail)
          break
        case 500:
          ElMessage.error('服务器错误: ' + errorDetail)
          break
        default:
          // 其他错误显示详细错误信息
          ElMessage.error(errorDetail)
      }
    } else {
      // 没有 response 且不是取消请求，才显示网络错误
      ElMessage.error('网络错误，请检查网络连接')
    }
    // 确保错误对象包含 detail 信息，方便调用方使用
    if (error.response && error.response.data) {
      error.detail = error.response.data.detail || error.response.data.message
    }
    return Promise.reject(error)
  }
)

// API接口
export const emailApi = {
  // 获取邮件列表
  getEmails: (params) => api.get('/emails', { params }),
  
  // 获取邮件详情
  getEmailDetail: (id) => api.get(`/emails/${encodeURIComponent(id)}`),
  
  // 处理邮件
  processEmail: (id) => api.post(`/emails/${encodeURIComponent(id)}/process`),
  
  // 重新检索（使用修改后的查询问题）
  reRetrieve: (id, queries) => api.post(`/emails/${encodeURIComponent(id)}/re-retrieve`, { queries }),
  
  // 处理全部邮件
  processAllEmails: () => api.post('/emails/process-all'),
  
  // 终止全部处理
  stopProcessAll: () => api.post('/emails/stop-process-all'),
  
  // 终止单封邮件处理
  stopProcessEmail: (id) => api.post(`/emails/${encodeURIComponent(id)}/stop-process`),
  
  // 发送回复（使用请求体传递邮件ID）
  sendReply: (id, reply) => api.post('/emails/send', { email_id: id, reply }),
  
  // 更新回复（编辑后保存，不发送）
  updateReply: (id, reply) => api.post('/emails/update-reply', { email_id: id, reply }),
  
  // 标记已读（使用请求体传递邮件ID）
  markAsRead: (id) => api.post('/emails/mark-read', { email_id: id }),
  
  // 删除邮件
  deleteEmail: (id) => api.delete(`/emails/${encodeURIComponent(id)}`),
  
  // 删除所有邮件
  deleteAllEmails: () => api.delete('/emails'),
  
  // 生成摘要
  generateSummary: (text) => api.post('/emails/summarize', { text })
}

export const systemApi = {
  // 获取系统状态
  getStatus: () => api.get('/system/status'),
  
  // 启动监控
  startMonitor: () => api.post('/system/start'),
  
  // 停止监控
  stopMonitor: () => api.post('/system/stop'),
  
  // 刷新邮件
  refreshEmails: () => api.post('/system/refresh'),
  
  // 开启/关闭自动处理
  setAutoProcess: (enable) => api.post('/system/auto-process', null, { params: { enable } })
}

export const statsApi = {
  // 获取统计数据
  getStats: () => api.get('/stats'),
  
  // 获取分类统计
  getCategoryStats: () => api.get('/stats/category'),
  
  // 获取趋势数据
  getTrendStats: (days = 7) => api.get('/stats/trend', { params: { days } })
}

export const historyApi = {
  // 获取处理记录
  getHistory: (params) => api.get('/history', { params }),
  
  // 导出记录
  exportHistory: (params) => api.get('/history/export', { params, responseType: 'blob' })
}

export const knowledgeApi = {
  // 获取文档列表
  getDocuments: () => api.get('/knowledge/documents'),
  
  // 上传文档
  uploadDocument: (file, autoIndex = false) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { auto_index: autoIndex }
    })
  },
  
  // 预览文档
  previewDocument: (id) => api.get(`/knowledge/documents/${encodeURIComponent(id)}/preview`),
  
  // 下载文档
  downloadDocument: (id) => api.get(`/knowledge/documents/${encodeURIComponent(id)}/download`, {
    responseType: 'blob'
  }),
  
  // 删除文档
  deleteDocument: (id) => api.delete(`/knowledge/documents/${encodeURIComponent(id)}`),
  
  // 重建索引（单个文档或全部，传入"all"重建全部）
  reindexDocument: (id) => api.post(`/knowledge/documents/${encodeURIComponent(id)}/reindex`),
  
  // RAG测试
  testRAG: (question, signal) => api.post('/knowledge/test', { question }, { signal }),
  
  // 取消RAG测试
  cancelRAGTest: () => api.post('/knowledge/test/cancel')
}

export const settingsApi = {
  // 获取设置
  getSettings: () => api.get('/settings'),
  
  // 保存设置
  saveSettings: (settings) => api.post('/settings', settings),
  
  // 测试邮箱连接
  testEmailConnection: (config) => api.post('/settings/test-email', config),
  
  // 测试AI连接
  testAIConnection: (config) => api.post('/settings/test-ai', config || {}),
  
  // 添加自定义模型
  addCustomModel: (model) => api.post('/settings/models', model),
  
  // 删除自定义模型
  deleteCustomModel: (modelId) => api.delete(`/settings/models/${modelId}`),
  
  // 获取自定义模型列表
  getCustomModels: () => api.get('/settings/models')
}

export const authApi = {
  // 检查用户名是否已存在
  checkUsername: (username) => api.get('/auth/check-username', { params: { username } }),
  
  // 用户注册
  register: (username, password, email) => api.post('/auth/register', {
    username,
    password,
    email
  }),
  
  // 获取用户资料
  getProfile: () => api.get('/auth/profile'),
  
  // 修改密码
  changePassword: (oldPassword, newPassword) => api.post('/auth/change-password', {
    oldPassword,
    newPassword
  }),
  
  // 忘记密码 - 验证用户名和邮箱
  forgotPassword: (username, email) => api.post('/auth/forgot-password', {
    username,
    email
  }),
  
  // 重置密码
  resetPassword: (username, email, newPassword) => api.post('/auth/reset-password', {
    username,
    email,
    newPassword
  }),
  
  // 更新用户资料
  updateProfile: (username) => api.post('/auth/update-profile', {
    username
  }),
  
  // 获取登录设备列表
  getDevices: () => api.get('/auth/devices'),
  
  // 下线设备
  logoutDevice: (deviceId) => api.post(`/auth/devices/${deviceId}/logout`),
  
  // 获取用户偏好设置
  getPreferences: () => api.get('/auth/preferences'),
  
  // 保存用户偏好设置
  savePreferences: (preferences) => api.post('/auth/preferences', preferences),
  
  // 获取最近操作
  getActivities: (limit = 10) => api.get('/activities', { params: { limit } })
}

export default api

