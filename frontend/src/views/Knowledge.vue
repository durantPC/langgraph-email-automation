<template>
  <div class="knowledge-page">
    <el-row :gutter="20">
      <!-- 文档列表 -->
      <el-col :xs="24" :lg="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>知识库文档 ({{ documents.length }})</span>
              <div style="display: flex; gap: 8px;">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索文档..."
                  clearable
                  style="width: 200px;"
                  @input="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-select
                  v-model="sortBy"
                  placeholder="排序"
                  style="width: 120px;"
                  @change="handleSort"
                >
                  <el-option label="更新时间" value="time" />
                  <el-option label="文件名称" value="name" />
                  <el-option label="文件大小" value="size" />
                </el-select>
                <el-upload
                  :show-file-list="false"
                  :before-upload="handleUpload"
                  accept=".txt,.pdf,.docx,.md"
                >
                  <el-button type="primary">
                    <el-icon><Plus /></el-icon>
                    添加文档
                  </el-button>
                </el-upload>
                <el-button type="warning" @click="reindexAll">
                  <el-icon><Refresh /></el-icon>
                  重建全部索引
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="document-list">
            <el-empty v-if="filteredDocuments.length === 0" :description="searchKeyword ? '未找到匹配的文档' : '暂无文档，请上传文档到知识库'" />
            <div v-for="doc in filteredDocuments" :key="doc.id" class="document-item">
              <div class="doc-icon">
                <el-icon :size="32" :color="getFileIconColor(doc.name)">
                  <component :is="getFileIcon(doc.name)" />
                </el-icon>
              </div>
              <div class="doc-info">
                <div class="doc-name" :title="doc.name">{{ doc.name }}</div>
                <div class="doc-meta">
                  <span>大小: {{ doc.size }}</span>
                  <span>更新: {{ doc.updateTime }}</span>
                  <span v-if="doc.chunkCount">片段: {{ doc.chunkCount }}</span>
                </div>
              </div>
              <div class="doc-status">
                <el-tag :type="doc.indexed ? 'success' : 'warning'" size="small">
                  {{ doc.indexed ? '已索引' : '未索引' }}
                </el-tag>
              </div>
              <div class="doc-actions">
                <el-button type="info" link size="small" @click="downloadDoc(doc)" title="下载文档">
                  <el-icon><Download /></el-icon>
                </el-button>
                <el-button type="primary" link size="small" @click="previewDoc(doc)" title="预览">
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button type="warning" link size="small" @click="reindexDoc(doc)" title="重建索引">
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-button type="danger" link size="small" @click="deleteDoc(doc)" title="删除">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- RAG测试 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :lg="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>RAG测试</span>
            </div>
          </template>
          
          <div class="rag-test">
            <el-input
              v-model="testQuestion"
              type="textarea"
              :rows="8"
              placeholder="输入问题测试RAG检索效果..."
              @input="saveRAGTestState"
              :style="{ fontSize: '14px', lineHeight: '1.6' }"
            />
            <div style="margin-top: 12px; display: flex; gap: 8px;">
              <el-button 
                type="primary" 
                :loading="testing"
                :disabled="testing"
                @click="handleTest"
              >
                <el-icon v-if="!testing"><Search /></el-icon>
                {{ testing ? '正在检索中...' : '测试检索' }}
              </el-button>
              <el-button 
                v-if="testing"
                type="danger"
                @click="handleCancel"
              >
                <el-icon><Close /></el-icon>
                终止检索
              </el-button>
            </div>
            
            <!-- 显示正在检索中的提示 -->
            <div v-if="testing && !testResult" class="test-result" style="margin-top: 16px;">
              <h4>检索结果</h4>
              <div class="result-content" style="text-align: center; padding: 20px; color: #909399;">
                <el-icon class="is-loading" style="font-size: 20px; margin-right: 8px;"><Loading /></el-icon>
                正在检索中，请稍候...
              </div>
            </div>
            
            <!-- 显示检索结果 -->
            <div v-if="testResult && !testing" class="test-result">
              <h4>检索结果</h4>
              <div class="result-content" :style="{ maxHeight: '400px', overflowY: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }">{{ testResult }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="文档预览" width="700px">
      <div class="preview-content">
        <pre>{{ previewContent }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { knowledgeApi } from '@/api'
import { Plus, Document, View, Refresh, Delete, Search, Loading, Download, Files, Paperclip, Close } from '@element-plus/icons-vue'

const testQuestion = ref('')
const testResult = ref('')
const testing = ref(false)
const previewVisible = ref(false)
const previewContent = ref('')

// 将 abortController 保存到全局 window 对象，避免组件卸载时丢失
// 这样即使切换页面，请求也不会被取消
const getAbortControllerKey = () => {
  const username = localStorage.getItem('username') || 'admin'
  return `rag_abort_controller_${username}`
}

const getAbortController = () => {
  const key = getAbortControllerKey()
  if (!window[key] || window[key].signal.aborted) {
    window[key] = new AbortController()
  }
  return window[key]
}

const clearAbortController = () => {
  const key = getAbortControllerKey()
  if (window[key]) {
    delete window[key]
  }
}

const documents = ref([])
const filteredDocuments = ref([])
const searchKeyword = ref('')
const sortBy = ref('time')
const route = useRoute()

// 持久化存储的key（按用户名隔离）
const getStorageKey = (key) => {
  const username = localStorage.getItem('username') || 'admin'
  return `knowledge_${key}_${username}`
}

// 保存RAG测试记录到localStorage
const saveRAGTestState = () => {
  try {
    localStorage.setItem(getStorageKey('testQuestion'), testQuestion.value)
    localStorage.setItem(getStorageKey('testResult'), testResult.value)
    // 保存检索状态和时间戳
    localStorage.setItem(getStorageKey('testing'), String(testing.value))
    if (testing.value) {
      localStorage.setItem(getStorageKey('testingStartTime'), String(Date.now()))
    } else {
      localStorage.removeItem(getStorageKey('testingStartTime'))
    }
  } catch (error) {
    console.error('保存RAG测试记录失败:', error)
  }
}

// 从localStorage恢复RAG测试记录
const loadRAGTestState = () => {
  try {
    const savedQuestion = localStorage.getItem(getStorageKey('testQuestion'))
    const savedResult = localStorage.getItem(getStorageKey('testResult'))
    const savedTesting = localStorage.getItem(getStorageKey('testing'))
    const savedTestingStartTime = localStorage.getItem(getStorageKey('testingStartTime'))
    
    console.log('🔍 [恢复状态]', {
      savedQuestion,
      savedResult: savedResult ? savedResult.substring(0, 50) + '...' : null,
      savedTesting,
      savedTestingStartTime
    })
    
    if (savedQuestion !== null) {  // 使用 !== null 而不是 truthy，允许空字符串
      testQuestion.value = savedQuestion
    }
    if (savedResult !== null && savedResult !== '') {  // 只恢复非空的结果
      testResult.value = savedResult
    }
    
    // 恢复检索状态 - 保持状态，等待 WebSocket 通知更新
    // 如果后台还在检索，保持 testing=true，等待 WebSocket 通知
    if (savedTesting === 'true') {
      if (savedTestingStartTime) {
        const startTime = parseInt(savedTestingStartTime)
        const elapsed = Date.now() - startTime
        const timeout = 5 * 60 * 1000 // 5分钟超时（给后台足够时间完成检索）
        
        if (elapsed > timeout) {
          // 超过5分钟，认为请求已失效，重置状态
          console.log('⏱️ [恢复状态] 检索已超时（超过5分钟），重置状态')
          testing.value = false
          localStorage.setItem(getStorageKey('testing'), 'false')
          localStorage.removeItem(getStorageKey('testingStartTime'))
        } else if (savedResult && savedResult !== '') {
          // 有结果了，说明检索已完成
          console.log('✅ [恢复状态] 检索已完成，有结果')
          testing.value = false
          localStorage.setItem(getStorageKey('testing'), 'false')
          localStorage.removeItem(getStorageKey('testingStartTime'))
        } else {
          // 时间在5分钟内且没有结果，保持检索状态，等待 WebSocket 通知
          console.log('🔄 [恢复状态] 保持检索状态，等待 WebSocket 通知（后台可能还在检索）')
          testing.value = true
          // 不重置状态，让 WebSocket 来更新
        }
      } else {
        // 没有时间戳，但有testing状态
        if (savedResult && savedResult !== '') {
          // 有结果，说明检索已完成
          console.log('✅ [恢复状态] 检索已完成（无时间戳但有结果）')
          testing.value = false
          localStorage.setItem(getStorageKey('testing'), 'false')
        } else {
          // 没有结果且没有时间戳，保持状态等待通知（可能是旧状态，但给一次机会）
          console.log('🔄 [恢复状态] 保持检索状态，等待 WebSocket 通知')
          testing.value = true
        }
      }
    } else {
      // 没有保存的testing状态，确保是false
      testing.value = false
    }
    
    console.log('📊 [恢复状态] 最终状态:', {
      testing: testing.value,
      hasResult: !!testResult.value,
      question: testQuestion.value
    })
  } catch (error) {
    console.error('❌ [恢复状态] 加载RAG测试记录失败:', error)
  }
}

// WebSocket 连接
let ws = null

// 建立 WebSocket 连接
const connectWebSocket = () => {
  // 如果已有连接，先关闭
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log('📡 [知识库] 关闭现有 WebSocket 连接')
    ws.close()
  }
  
  // 从 localStorage 获取 token
  const token = localStorage.getItem('token')
  const wsUrl = token 
    ? `ws://localhost:8000/api/ws?token=${encodeURIComponent(token)}`
    : 'ws://localhost:8000/api/ws'
  
  console.log('📡 [知识库] 正在连接 WebSocket:', wsUrl)
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('📡 [知识库] WebSocket 连接已建立')
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('📨 [知识库] 收到 WebSocket 消息:', data)
      
      // 处理 RAG 测试完成通知
      if (data.type === 'rag_test_complete') {
        console.log('✅ [知识库] 收到 RAG 测试完成通知:', {
          question: data.question,
          success: data.success,
          cancelled: data.cancelled
        })
        
        // 检查问题是否匹配（避免处理其他用户的检索结果）
        // 如果 testQuestion 为空，说明可能是切换页面后恢复的状态，也接受通知
        const questionMatches = data.question === testQuestion.value || 
                                !testQuestion.value || 
                                testQuestion.value === ''
        
        if (questionMatches) {
          console.log('✅ [知识库] 收到匹配的 RAG 测试结果，更新状态')
          
          // 更新问题（如果当前问题为空，使用通知中的问题）
          if (!testQuestion.value && data.question) {
            testQuestion.value = data.question
          }
          
          // 更新状态（统一由 WebSocket 通知更新）
          testing.value = false
          if (data.answer) {
            testResult.value = data.answer
          }
          
          // 保存状态
          saveRAGTestState()
          
          // 使用 localStorage 协调多个标签页，确保只有一个标签页显示提示
          const messageKey = `rag_test_complete_${data.question || 'default'}`
          const lastShownTime = localStorage.getItem(messageKey)
          const now = Date.now()
          
          // 如果1秒内已经显示过提示，跳过（说明其他标签页已经显示了）
          if (lastShownTime && (now - parseInt(lastShownTime)) < 1000) {
            console.log('⚠️ [知识库] 跳过显示提示（其他标签页已显示）')
          } else {
            // 记录显示时间
            localStorage.setItem(messageKey, now.toString())
            // 1秒后清除记录
            setTimeout(() => {
              localStorage.removeItem(messageKey)
            }, 1000)
            
            // 显示提示
            if (data.cancelled) {
              ElMessage.info('检索已取消')
            } else if (data.success) {
              ElMessage.success('检索完成')
            } else {
              ElMessage.warning('检索失败')
            }
          }
        } else {
          console.log('⚠️ [知识库] 收到其他问题的检索结果，忽略:', {
            received: data.question,
            current: testQuestion.value
          })
        }
      }
    } catch (e) {
      console.error('❌ [知识库] 解析 WebSocket 消息失败:', e)
    }
  }
  
  ws.onclose = () => {
    console.log('📡 [知识库] WebSocket 连接已断开，5秒后重连...')
    setTimeout(connectWebSocket, 5000)
  }
  
  ws.onerror = (error) => {
    console.error('📡 [知识库] WebSocket 错误:', error)
  }
}

// 获取文档列表
const fetchDocuments = async () => {
  try {
    const res = await knowledgeApi.getDocuments()
    documents.value = res.documents || []
    applyFilters()
  } catch (e) {
    console.error('获取文档列表失败', e)
    documents.value = [
      { id: 'agency.txt', name: 'agency.txt', size: '2.5KB', updateTime: '2025-11-20', indexed: true }
    ]
    applyFilters()
  }
}

// 获取文件图标
const getFileIcon = (filename) => {
  const ext = filename.split('.').pop()?.toLowerCase()
  if (['txt', 'md'].includes(ext)) return Document
  if (ext === 'pdf') return Files
  if (['doc', 'docx'].includes(ext)) return Document
  return Paperclip
}

// 获取文件图标颜色
const getFileIconColor = (filename) => {
  const ext = filename.split('.').pop()?.toLowerCase()
  if (['txt', 'md'].includes(ext)) return '#409eff'
  if (ext === 'pdf') return '#f56c6c'
  if (['doc', 'docx'].includes(ext)) return '#67c23a'
  return '#909399'
}

// 搜索文档
const handleSearch = () => {
  applyFilters()
}

// 排序文档
const handleSort = () => {
  applyFilters()
}

// 应用过滤和排序
const applyFilters = () => {
  let result = [...documents.value]
  
  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(doc => doc.name.toLowerCase().includes(keyword))
  }
  
  // 排序
  if (sortBy.value === 'name') {
    result.sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'size') {
    result.sort((a, b) => {
      const sizeA = parseFloat(a.size) || 0
      const sizeB = parseFloat(b.size) || 0
      return sizeB - sizeA
    })
  } else {
    // 默认按时间排序
    result.sort((a, b) => {
      const timeA = new Date(a.updateTime).getTime() || 0
      const timeB = new Date(b.updateTime).getTime() || 0
      return timeB - timeA
    })
  }
  
  filteredDocuments.value = result
}

// 下载文档
const downloadDoc = async (doc) => {
  try {
    const res = await knowledgeApi.downloadDocument(doc.id)
    // 创建下载链接
    const blob = new Blob([res], { type: 'application/octet-stream' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = doc.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

onMounted(() => {
  fetchDocuments()
  loadRAGTestState() // 恢复RAG测试记录
  
  // 建立 WebSocket 连接
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    connectWebSocket()
  }
  
  // 初始化过滤后的文档列表
  applyFilters()
})

// 使用 onActivated 确保从其他页面返回时也恢复数据（keep-alive场景）
onActivated(() => {
  loadRAGTestState() // 恢复RAG测试记录
  
  // 确保 WebSocket 连接
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    connectWebSocket()
  }
})

// 监听路由变化，当进入知识库页面时恢复数据（非keep-alive场景）
watch(() => route.path, (newPath) => {
  if (newPath === '/knowledge') {
    loadRAGTestState() // 恢复RAG测试记录
  }
}, { immediate: false })

// 监听testing状态变化，立即保存
watch(testing, (newVal, oldVal) => {
  console.log('🔄 [状态变化] testing:', oldVal, '->', newVal)
  saveRAGTestState()
}, { immediate: false })

// 监听testResult变化，立即保存
watch(testResult, (newVal, oldVal) => {
  console.log('📝 [结果变化] testResult:', oldVal ? oldVal.substring(0, 30) + '...' : 'null', '->', newVal ? newVal.substring(0, 30) + '...' : 'null')
  saveRAGTestState()
}, { immediate: false })

// 页面卸载前保存状态（但不取消请求，让检索在后台继续）
onBeforeUnmount(() => {
  // 只保存状态，不取消请求，这样即使用户切换页面，检索也会在后台继续
  // 当用户返回页面时，可以通过 localStorage 恢复状态，并通过 WebSocket 接收更新
  saveRAGTestState()
  // 不关闭 WebSocket，让它在后台继续接收消息
})

const handleUpload = async (file) => {
  try {
    // 验证文件类型
    const allowedTypes = ['.txt', '.pdf', '.docx', '.md']
    const fileExt = '.' + file.name.split('.').pop().toLowerCase()
    if (!allowedTypes.includes(fileExt)) {
      ElMessage.error(`不支持的文件类型: ${fileExt}，支持的类型: ${allowedTypes.join(', ')}`)
      return false
    }
    
    // 验证文件大小（限制10MB）
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      ElMessage.error(`文件过大，最大支持 10MB`)
      return false
    }
    
    // 询问是否自动重建索引（仅对.txt和.md文件）
    let autoIndex = false
    if (['.txt', '.md'].includes(fileExt)) {
      try {
        await ElMessageBox.confirm(
          '上传后是否自动重建索引？\n（重建索引可能需要1-2分钟）',
          '提示',
          {
            confirmButtonText: '自动重建',
            cancelButtonText: '稍后手动重建',
            type: 'info'
          }
        )
        autoIndex = true
      } catch {
        autoIndex = false
      }
    }
    
    ElMessage.info(`正在上传 ${file.name}...`)
    const res = await knowledgeApi.uploadDocument(file, autoIndex)
    
    if (autoIndex && res.indexing) {
      ElMessage.success(`文件 ${file.name} 上传成功，正在后台重建索引...`)
    } else {
      ElMessage.success(`文件 ${file.name} 上传成功`)
      if (['.txt', '.md'].includes(fileExt)) {
        ElMessage.info('请点击"重建索引"按钮更新向量索引')
      }
    }
    
    await fetchDocuments()
    // 清空搜索，显示新上传的文档
    searchKeyword.value = ''
    applyFilters()
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '上传失败')
  }
  return false
}

const previewDoc = async (doc) => {
  try {
    previewVisible.value = true
    previewContent.value = '正在加载文档内容...'
    
    const res = await knowledgeApi.previewDocument(doc.id)
    if (res.previewable) {
      previewContent.value = res.content
    } else {
      previewContent.value = res.content || '无法预览此文件'
    }
  } catch (error) {
    console.error('预览失败:', error)
    previewContent.value = error.response?.data?.detail || error.message || '预览失败'
  }
}

const reindexDoc = async (doc) => {
  ElMessage.info(`正在重建 ${doc.name} 的索引...`)
  try {
    const res = await knowledgeApi.reindexDocument(doc.id)
    // 更新文档状态
    const docIndex = documents.value.findIndex(d => d.id === doc.id)
    if (docIndex !== -1) {
      documents.value[docIndex].indexed = true
    }
    applyFilters() // 更新过滤后的列表
    ElMessage.success(res.message || '索引重建任务已启动，正在后台执行...')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || e.message || '重建索引失败')
  }
}

const reindexAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重建全部索引吗？\n（这将重建所有文档的向量索引，可能需要1-2分钟）',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.info('正在重建全部索引...')
    const res = await knowledgeApi.reindexDocument('all')
    ElMessage.success(res.message || '全部索引重建任务已启动，正在后台执行...')
    
    // 更新所有文档状态
    documents.value.forEach(doc => {
      doc.indexed = true
    })
    applyFilters()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || e.message || '重建索引失败')
    }
  }
}

const deleteDoc = (doc) => {
  ElMessageBox.confirm(`确定要删除 ${doc.name} 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await knowledgeApi.deleteDocument(doc.id)
      documents.value = documents.value.filter(d => d.id !== doc.id)
      applyFilters() // 更新过滤后的列表
      ElMessage.success('删除成功')
    } catch (e) {
      console.error('删除失败:', e)
      const errorMsg = e.response?.data?.detail || e.message || '删除失败'
      ElMessage.error(`删除失败: ${errorMsg}`)
    }
  }).catch(() => {})
}

const handleTest = async () => {
  if (!testQuestion.value.trim()) {
    ElMessage.warning('请输入测试问题')
    return
  }
  
  // 如果已有请求在进行，先取消
  const existingController = getAbortController()
  if (existingController && !existingController.signal.aborted) {
    existingController.abort()
  }
  
  // 创建新的 AbortController（保存到全局）
  const newController = new AbortController()
  const key = getAbortControllerKey()
  window[key] = newController
  
  console.log('🚀 [开始检索] 点击检索按钮')
  
  // 先清空旧结果（但保留在变量中，不立即保存）
  const oldResult = testResult.value
  testResult.value = ''  // 清空结果，准备显示新的检索状态
  
  // 设置检索状态
  testing.value = true
  console.log('🔄 [开始检索] testing设置为true')
  
  // 立即保存状态（watch会自动触发，但这里也显式调用确保保存）
  saveRAGTestState()
  console.log('💾 [开始检索] 状态已保存到localStorage')
  
  try {
    const controller = getAbortController()
    const res = await knowledgeApi.testRAG(testQuestion.value, controller.signal)
    console.log('✅ [检索完成] 收到响应:', {
      success: res.success,
      answerLength: res.answer ? res.answer.length : 0,
      answerPreview: res.answer ? res.answer.substring(0, 100) : 'null'
    })
    
    if (res.success) {
      // 确保结果不为空
      const answer = res.answer || '未找到相关信息'
      testResult.value = answer
      testing.value = false  // 请求成功，立即更新状态
      console.log('📝 [检索完成] 设置testResult.value:', answer.substring(0, 100) + '...')
    } else {
      testResult.value = res.answer || '检索失败'
      testing.value = false  // 请求失败，立即更新状态
      ElMessage.warning('检索失败，请查看结果详情')
    }
    
    // 保存结果到localStorage
    saveRAGTestState()
    console.log('💾 [检索完成] 结果已保存，testResult.value长度:', testResult.value.length)
  } catch (e) {
    // 检查是否是取消请求（包括 axios 拦截器设置的标记）
    if (e.isCanceled || e.name === 'AbortError' || e.message === 'canceled' || e.code === 'ERR_CANCELED' || e.code === 'ERR_ABORTED') {
      console.log('🚫 [检索取消] 用户取消了检索（前端请求已取消）')
      // 前端请求已取消，但后端可能还在检索
      // 不在这里更新状态，等待后端通过 WebSocket 通知统一更新
      // 这样确保状态更新的一致性
      console.log('⏳ [检索取消] 等待后端 WebSocket 通知更新状态')
      // 不更新状态，不显示消息，等待 WebSocket 通知
    } else {
      console.error('❌ [检索失败]', e)
      // 请求失败（非取消），立即更新状态（这是正常的 HTTP 错误响应）
      testing.value = false
      testResult.value = e.response?.data?.detail || e.detail || e.message || '检索失败，请检查后端服务是否正常'
      saveRAGTestState()
      ElMessage.error('检索失败')
    }
    
    console.log('💾 [检索失败] 错误信息已保存')
  } finally {
    // 注意：testing.value 已经在 try 或 catch 块中更新了
    // 如果请求被取消但后端还在检索，WebSocket 会通知最终状态
    // 这里只保存状态，不修改 testing.value
    console.log('🔄 [检索完成] 最终保存状态')
    saveRAGTestState()
    console.log('💾 [检索完成] 最终状态已保存')
  }
}

const handleCancel = async () => {
  const controller = getAbortController()
  if (controller && !controller.signal.aborted) {
    console.log('🚫 [取消检索] 用户点击了取消按钮')
    
    // 1. 取消前端请求
    controller.abort()
    clearAbortController()
    
    // 2. 通知后端取消检索
    try {
      await knowledgeApi.cancelRAGTest()
      console.log('✅ [取消检索] 已通知后端取消检索')
    } catch (e) {
      console.warn('⚠️ [取消检索] 通知后端失败，但前端已取消:', e)
    }
    
    // 3. 不在这里更新状态，等待后端通过 WebSocket 通知统一更新
    // 这样确保状态更新的一致性，避免重复更新
    console.log('⏳ [取消检索] 等待后端 WebSocket 通知更新状态')
  }
}
</script>

<style lang="scss" scoped>
.knowledge-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .document-list {
    .document-item {
      display: flex;
      align-items: center;
      padding: 16px;
      border-bottom: 1px solid #ebeef5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .doc-icon {
        margin-right: 16px;
      }
      
      .doc-info {
        flex: 1;
        
        .doc-name {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
        }
        
        .doc-meta {
          font-size: 12px;
          color: #909399;
          margin-top: 4px;
          
          span {
            margin-right: 16px;
          }
        }
      }
      
      .doc-status {
        margin-right: 16px;
      }
      
      .doc-actions {
        display: flex;
        gap: 8px;
      }
    }
  }
  
  .rag-test {
    .test-result {
      margin-top: 20px;
      
      h4 {
        font-size: 14px;
        color: #303133;
        margin: 0 0 12px;
      }
      
      .result-content {
        padding: 16px;
        background-color: #f0f9eb;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.8;
        white-space: pre-wrap;
        word-break: break-word;
        max-height: 400px;
        overflow-y: auto;
        color: #303133;
      }
    }
  }
  
  .preview-content {
    pre {
      background-color: #f5f7fa;
      padding: 16px;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.8;
      white-space: pre-wrap;
      max-height: 400px;
      overflow-y: auto;
    }
  }
}
</style>

