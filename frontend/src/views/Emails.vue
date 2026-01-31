<template>
  <div class="emails-page">
    <!-- 顶部操作栏 -->
    <el-card shadow="hover" class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" @click="handleRefresh" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新邮件
          </el-button>
          <el-button type="success" @click="handleProcessAll" :disabled="pendingEmails.length === 0 || isProcessingAll || systemStatus.autoProcess || hasProcessingEmails || loading" :loading="isProcessingAll">
            <el-icon v-if="!isProcessingAll"><VideoPlay /></el-icon>
            {{ isProcessingAll ? 'AI处理中...' : 'AI处理全部' }}
          </el-button>
          <el-button 
            v-if="isProcessingAll || systemStatus.autoProcess || isStoppingAll"
            type="danger"
            :disabled="isStoppingAll"
            :loading="isStoppingAll"
            @click="handleStopProcessing"
          >
            <el-icon v-if="!isStoppingAll"><Close /></el-icon>
            {{ isStoppingAll ? '正在终止全部...' : '终止处理' }}
          </el-button>
          <el-button type="danger" @click="handleDeleteAll" :disabled="emails.length === 0 || loading">
            <el-icon><Delete /></el-icon>
            清空全部
          </el-button>
        </div>
        
        <div class="toolbar-right">
          <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="未处理" value="pending" />
            <el-option label="已处理" value="processed" />
          </el-select>
          <el-select v-model="filterCategory" placeholder="分类筛选" clearable style="width: 120px">
            <el-option label="全部" value="" />
            <el-option label="产品咨询" value="product_enquiry" />
            <el-option label="客户投诉" value="customer_complaint" />
            <el-option label="客户反馈" value="customer_feedback" />
            <el-option label="无关邮件" value="unrelated" />
          </el-select>
          <el-input 
            v-model="searchKeyword" 
            placeholder="搜索邮件..." 
            style="width: 200px"
            :prefix-icon="Search"
            clearable
          />
        </div>
      </div>
    </el-card>
    
    <!-- 邮件列表 -->
    <el-row :gutter="20">
      <!-- 邮件列表 -->
      <el-col :xs="24" :lg="selectedEmail ? 12 : 24">
        <el-card shadow="hover" class="email-list-card">
          <template #header>
            <div class="card-header">
              <span>邮件列表</span>
              <el-tag type="info" size="small">共 {{ filteredEmails.length }} 封</el-tag>
            </div>
          </template>
          
          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading" :size="40"><Loading /></el-icon>
            <p>正在加载邮件...</p>
          </div>
          
          <div v-else-if="filteredEmails.length === 0" class="empty-container">
            <el-empty description="暂无邮件" />
          </div>
          
          <div v-else class="email-list">
            <div 
              v-for="email in paginatedEmails" 
              :key="email.id"
              class="email-item"
              :class="{ 
                'is-selected': selectedEmail?.id === email.id,
                'is-unread': email.status === 'pending' || email.status === 'processing'
              }"
              @click="selectEmail(email)"
            >
              <div class="email-status">
                <el-icon v-if="email.status === 'pending' || email.status === 'processing'" color="#e6a23c"><Clock /></el-icon>
                <el-icon v-else-if="email.status === 'processed'" color="#67c23a"><CircleCheck /></el-icon>
                <el-icon v-else color="#f56c6c"><CircleClose /></el-icon>
              </div>
              
              <div class="email-content">
                <div class="email-header">
                  <span class="email-sender">{{ email.sender }}</span>
                  <span class="email-time">{{ email.time }}</span>
                </div>
                <div class="email-subject">{{ email.subject }}</div>
                <div class="email-preview">{{ email.preview }}</div>
                <div class="email-tags">
                  <el-tag 
                    v-if="email.category" 
                    :type="getCategoryType(email.category)" 
                    size="small"
                  >
                    {{ getCategoryLabel(email.category) }}
                  </el-tag>
                  <el-tag 
                    v-if="email.urgency_level && email.urgency_level !== 'low'" 
                    :type="getUrgencyType(email.urgency_level)" 
                    size="small"
                    style="margin-left: 4px;"
                  >
                    {{ getUrgencyLabel(email.urgency_level) }}
                  </el-tag>
                </div>
              </div>
              
              <div class="email-actions">
                <el-button 
                  v-if="email.status === 'pending' || email.status === 'processing'"
                  type="primary" 
                  size="small"
                  :loading="email.processing || email.status === 'processing'"
                  :disabled="isProcessingAll || systemStatus.autoProcess || email.status === 'processing' || email.processing"
                  @click.stop="handleProcess(email)"
                >
                  {{ (email.processing || email.status === 'processing') ? 'AI处理中...' : 'AI处理' }}
                </el-button>
                <el-button 
                  v-if="email.status === 'processing' || email.status === 'stopping' || email.processing"
                  type="danger" 
                  size="small"
                  :disabled="email.status === 'stopping' || isProcessingAll || isStoppingAll"
                  :loading="email.status === 'stopping'"
                  @click.stop="handleStopSingleEmail(email)"
                >
                  <el-icon v-if="email.status !== 'stopping'"><Close /></el-icon>
                  {{ email.status === 'stopping' ? '正在终止...' : '终止' }}
                </el-button>
                <el-button 
                  v-if="email.status === 'pending' && !email.processing"
                  type="info" 
                  size="small"
                  @click.stop="handleMarkRead(email)"
                >
                  已读
                </el-button>
                <el-tag v-if="email.status === 'processed'" type="success" size="small">已处理</el-tag>
                <el-tag v-if="email.status === 'skipped'" type="warning" size="small">已跳过</el-tag>
                <el-tag v-if="email.status === 'failed'" type="danger" size="small">处理失败</el-tag>
                <el-button 
                  v-if="email.status === 'processed' || email.status === 'skipped' || email.status === 'failed'"
                  type="danger" 
                  size="small"
                  :icon="Delete"
                  @click.stop="handleDelete(email)"
                >
                  删除
                </el-button>
              </div>
            </div>
            
            <!-- 分页组件 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[5, 10, 20, 50, 100]"
                :total="filteredEmails.length"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 邮件详情 -->
      <el-col v-if="selectedEmail" :xs="24" :lg="12">
        <el-card shadow="hover" class="email-detail-card">
          <template #header>
            <div class="card-header">
              <span>邮件详情</span>
              <el-button type="info" link @click="selectedEmail = null">
                <el-icon><Close /></el-icon>
                关闭
              </el-button>
            </div>
          </template>
          
          <div class="email-detail">
            <div class="detail-header">
              <h3 class="detail-subject">{{ selectedEmail.subject }}</h3>
              <div class="detail-meta">
                <div class="meta-item">
                  <el-icon><User /></el-icon>
                  <span>{{ selectedEmail.sender }}</span>
                </div>
                <div class="meta-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ selectedEmail.time }}</span>
                </div>
                <el-tag 
                  v-if="selectedEmail.status === 'processing' || selectedEmail.processing" 
                  type="info" 
                  size="small"
                  :loading="true"
                >
                  AI处理中...
                </el-tag>
                <el-tag 
                  v-else-if="selectedEmail.category" 
                  :type="getCategoryType(selectedEmail.category)" 
                  size="small"
                >
                  {{ getCategoryLabel(selectedEmail.category) }}
                </el-tag>
                <el-tag 
                  v-if="selectedEmail.urgency_level && selectedEmail.urgency_level !== 'low'" 
                  :type="getUrgencyType(selectedEmail.urgency_level)" 
                  size="small"
                  style="margin-left: 4px;"
                >
                  {{ getUrgencyLabel(selectedEmail.urgency_level) }}
                </el-tag>
                <!-- 显示触发紧急程度的关键词 -->
                <el-tooltip
                  v-if="selectedEmail.urgency_keywords && selectedEmail.urgency_keywords.length > 0"
                  :content="'触发关键词: ' + selectedEmail.urgency_keywords.join(', ')"
                  placement="top"
                >
                  <el-tag 
                    type="info" 
                    size="small"
                    style="margin-left: 4px; cursor: help;"
                  >
                    <el-icon><Warning /></el-icon>
                    关键词触发
                  </el-tag>
                </el-tooltip>
              </div>
            </div>
            
            <el-divider />
            
            <div class="detail-section">
              <div class="section-header">
                <h4>
                  <el-icon><Message /></el-icon>
                  原始邮件内容
                </h4>
                <el-button 
                  type="primary" 
                  link 
                  size="small" 
                  @click="toggleFullContent('body')"
                >
                  {{ showFullBody ? '收起' : '展开全文' }}
                </el-button>
              </div>
              <div class="summary-box" v-if="!showFullBody">
                <div class="summary-content">
                  <div class="summary-text" v-if="emailSummary.body">
                    {{ emailSummary.body }}
                  </div>
                  <div v-else class="summary-loading">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>正在生成摘要...</span>
                  </div>
                </div>
                <div class="summary-hint">点击"展开全文"查看完整内容</div>
              </div>
              <div v-show="showFullBody" class="detail-body">
                {{ selectedEmail.body }}
              </div>
            </div>
            
            <!-- RAG 查询问题显示（可编辑） -->
            <el-divider v-if="selectedEmail.rag_queries && selectedEmail.rag_queries.length > 0" />
            
            <div v-if="selectedEmail.rag_queries && selectedEmail.rag_queries.length > 0" class="detail-section">
              <div class="section-header">
                <h4>
                  <el-icon><Search /></el-icon>
                  知识库查询问题
                </h4>
                <div class="section-actions">
                  <el-tag type="info" size="small">共 {{ selectedEmail.rag_queries.length }} 个</el-tag>
                  <el-button 
                    type="primary" 
                    size="small" 
                    :loading="isRetrieving"
                    :disabled="isRetrieving"
                    @click="handleReRetrieve"
                  >
                    <el-icon v-if="!isRetrieving"><Refresh /></el-icon>
                    {{ isRetrieving ? '检索中...' : '重新检索' }}
                  </el-button>
                </div>
              </div>
              <div class="rag-queries-box">
                <el-alert 
                  title="你可以修改下面的问题，然后点击【重新检索】来获取更准确的回复" 
                  type="warning" 
                  :closable="false"
                  show-icon
                  style="margin-bottom: 15px"
                />
                <div 
                  v-for="(query, index) in editableRagQueries" 
                  :key="index"
                  class="rag-query-item editable"
                >
                  <div class="query-number">问题 {{ index + 1 }}</div>
                  <el-input
                    v-model="editableRagQueries[index]"
                    type="textarea"
                    :autosize="{ minRows: 1, maxRows: 4 }"
                    placeholder="请输入查询问题..."
                    class="query-input"
                  />
                </div>
              </div>
            </div>
            
            <!-- 已处理、已发送或已跳过的邮件才显示回复内容 -->
            <el-divider v-if="selectedEmail.reply && (selectedEmail.status === 'processed' || selectedEmail.status === 'sent' || selectedEmail.status === 'skipped')" />
            
            <div v-if="selectedEmail.reply && (selectedEmail.status === 'processed' || selectedEmail.status === 'sent' || selectedEmail.status === 'skipped')" class="detail-section">
              <div class="section-header">
                <h4>
                  <el-icon><ChatDotRound /></el-icon>
                  AI生成的回复
                </h4>
                <el-button 
                  type="primary" 
                  link 
                  size="small" 
                  @click="toggleFullContent('reply')"
                >
                  {{ showFullReply ? '收起' : '展开全文' }}
                </el-button>
              </div>
              <div class="summary-box" v-if="!showFullReply">
                <div class="summary-content">
                  <div class="summary-text" v-if="emailSummary.reply">
                    {{ emailSummary.reply }}
                  </div>
                  <div v-else class="summary-loading">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>正在生成摘要...</span>
                  </div>
                </div>
                <div class="summary-hint">点击"展开全文"查看完整内容</div>
              </div>
              <div v-show="showFullReply" class="detail-reply">
                {{ selectedEmail.reply }}
              </div>
            </div>
            
            <div class="detail-actions">
              <el-button 
                v-if="selectedEmail.status === 'pending'"
                type="primary"
                :disabled="isProcessingAll || systemStatus.autoProcess || selectedEmail.status === 'processing' || selectedEmail.processing"
                :loading="selectedEmail.processing || selectedEmail.status === 'processing'"
                @click="handleProcess(selectedEmail)"
              >
                <el-icon><VideoPlay /></el-icon>
                {{ (selectedEmail.processing || selectedEmail.status === 'processing') ? 'AI处理中...' : 'AI处理此邮件' }}
              </el-button>
              <el-button 
                v-if="selectedEmail.reply && selectedEmail.status !== 'sent'"
                type="success"
                :loading="selectedEmail.sending"
                :disabled="selectedEmail.sending"
                @click="handleSendReply(selectedEmail)"
              >
                <el-icon v-if="!selectedEmail.sending"><Promotion /></el-icon>
                {{ selectedEmail.sending ? '发送中...' : '发送回复' }}
              </el-button>
              <el-tag v-if="selectedEmail.status === 'sent'" type="success">已发送</el-tag>
              <el-button 
                v-if="selectedEmail.status !== 'sent'"
                @click="handleEditReply(selectedEmail)"
              >
                <el-icon><Edit /></el-icon>
                编辑回复
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 编辑回复对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑回复" width="600px">
      <el-input
        v-model="editingReply"
        type="textarea"
        :rows="10"
        placeholder="请输入回复内容..."
      />
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveReply">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, onActivated } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { emailApi, systemApi, settingsApi } from '@/api'
import {
  Refresh, VideoPlay, Search, Clock, CircleCheck, CircleClose,
  Close, User, Message, ChatDotRound, Promotion, Edit, Loading, Delete,
  Warning
} from '@element-plus/icons-vue'

const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const filterCategory = ref('')
const selectedEmail = ref(null)
const editDialogVisible = ref(false)
const editingReply = ref('')

// RAG 查询编辑相关
const editableRagQueries = ref([])
const isRetrieving = ref(false)

// 摘要相关状态
const showFullBody = ref(false)
const showFullReply = ref(false)
const emailSummary = reactive({
  body: '',
  reply: '',
  bodyStatus: 'none',  // 'none' | 'generating' | 'ready'
  replyStatus: 'none'  // 'none' | 'generating' | 'ready'
})

// 分页相关（从localStorage读取保存的每页数量）
const currentPage = ref(1)
const pageSize = ref(parseInt(localStorage.getItem('email_page_size') || '10', 10))

// 全局处理状态（防止同时处理多个邮件）
const isProcessing = ref(false)

// 系统状态（用于判断是否开启了自动处理）
const systemStatus = ref({
  running: false,
  autoProcess: false
})

// 获取系统状态
const fetchSystemStatus = async () => {
  try {
    const res = await systemApi.getStatus()
    systemStatus.value.running = res.running
    systemStatus.value.autoProcess = res.autoProcess
  } catch (e) {
    console.error('获取系统状态失败', e)
  }
}

// WebSocket 连接
let ws = null
// 用于防止重复处理同一条消息
const processedMessageIds = new Set()

// 建立 WebSocket 连接
const connectWebSocket = () => {
  // 如果已有连接，先关闭
  if (ws && ws.readyState === WebSocket.OPEN) {
    console.log('关闭现有 WebSocket 连接')
    ws.close()
  }
  
  // 从 localStorage 获取 token
  const token = localStorage.getItem('token')
  const wsUrl = token 
    ? `ws://localhost:8000/api/ws?token=${encodeURIComponent(token)}`
    : 'ws://localhost:8000/api/ws'
  
  console.log('正在连接 WebSocket:', wsUrl)
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket 连接已建立')
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('收到 WebSocket 消息:', data)
      
      // 处理全部邮件完成通知（手动点击"处理全部"按钮）
      if (data.type === 'process_all_complete') {
        // 防止重复处理同一条消息
        const processAllKey = `process_all_${Date.now()}`
        const recentProcessAllKey = 'process_all_recent'
        
        // 检查最近5秒内是否处理过相同的消息
        if (processedMessageIds.has(recentProcessAllKey)) {
          console.log('忽略重复的 process_all_complete 消息')
          return
        }
        
        processedMessageIds.add(recentProcessAllKey)
        // 5秒后清除
        setTimeout(() => {
          processedMessageIds.delete(recentProcessAllKey)
        }, 5000)
        
        isProcessing.value = false
        // 延迟重置标志，确保所有单封邮件的消息都到达后再重置（延迟30秒，确保所有消息都到达）
        setTimeout(() => {
          isProcessingAll.value = false
          processAllStartTime.value = 0
          localStorage.removeItem('process_all_start_time')
          console.log('[WebSocket消息处理] 已重置处理全部邮件标志')
        }, 30000)
        
        // 立即清除所有邮件的 processing 状态，防止显示"AI处理中..."
        emails.value.forEach(email => {
          if (email.status === 'processing' || email.processing) {
            email.processing = false
            // 如果状态还是 processing，先设置为 processed（刷新后会从服务器获取正确状态）
            if (email.status === 'processing') {
              email.status = 'processed'
            }
          }
        })
        // 如果当前选中的邮件也在处理中，也要清除
        if (selectedEmail.value && (selectedEmail.value.status === 'processing' || selectedEmail.value.processing)) {
          selectedEmail.value.processing = false
          if (selectedEmail.value.status === 'processing') {
            selectedEmail.value.status = 'processed'
          }
        }
        
        // 使用 localStorage 协调多个标签页，确保只有一个标签页显示提示
        const messageKey = `process_all_complete_${Date.now()}`
        const lastShownTime = localStorage.getItem('process_all_complete_last')
        const now = Date.now()
        
        // 如果1秒内已经显示过提示，跳过（说明其他标签页已经显示了）
        if (lastShownTime && (now - parseInt(lastShownTime)) < 1000) {
          console.log('[WebSocket消息处理] 跳过显示 process_all_complete 提示（其他标签页已显示）')
        } else {
          // 记录显示时间
          localStorage.setItem('process_all_complete_last', now.toString())
          // 1秒后清除记录
          setTimeout(() => {
            localStorage.removeItem('process_all_complete_last')
          }, 1000)
          
          ElMessage.success(data.message)
        }
        // 刷新邮件列表（使用防抖机制，避免短时间内多次刷新）
        if (fetchTimer) {
          clearTimeout(fetchTimer)
        }
        fetchTimer = setTimeout(() => {
          fetchEmails(true).then(() => {
            // 刷新后，再次确保所有 processing 状态的邮件都被清除
            emails.value.forEach(email => {
              if (email.status === 'processing' || email.processing) {
                email.processing = false
                // 如果服务器返回的状态还是 processing（不应该发生），强制设置为 processed
                if (email.status === 'processing') {
                  email.status = 'processed'
                }
              }
            })
            // 如果当前选中的邮件也在处理中，也要清除
            if (selectedEmail.value && (selectedEmail.value.status === 'processing' || selectedEmail.value.processing)) {
              const refreshedEmail = emails.value.find(e => e.id === selectedEmail.value.id)
              if (refreshedEmail) {
                selectedEmail.value = refreshedEmail
              } else {
                selectedEmail.value.processing = false
                if (selectedEmail.value.status === 'processing') {
                  selectedEmail.value.status = 'processed'
                }
              }
            }
          })
          // 延迟通知其他页面刷新统计数据，避免请求冲突
          setTimeout(() => {
            window.dispatchEvent(new CustomEvent('stats-refresh'))
          }, 500)
        }, 500)
      }
      
      // 检测到新邮件通知（半自动模式）
      if (data.type === 'new_emails') {
        // 使用 localStorage 协调多个标签页，确保只有一个标签页显示提示
        const lastShownTime = localStorage.getItem('new_emails_last')
        const now = Date.now()
        
        // 如果1秒内已经显示过提示，跳过（说明其他标签页已经显示了）
        if (lastShownTime && (now - parseInt(lastShownTime)) < 1000) {
          // 跳过显示
        } else {
          // 记录显示时间
          localStorage.setItem('new_emails_last', now.toString())
          // 1秒后清除记录
          setTimeout(() => {
            localStorage.removeItem('new_emails_last')
          }, 1000)
          
          ElMessage.info(data.message)
        }
        // 刷新邮件列表（使用防抖机制）
        if (fetchTimer) {
          clearTimeout(fetchTimer)
        }
        fetchTimer = setTimeout(() => {
          fetchEmails(true)
          // 延迟通知其他页面刷新统计数据
          setTimeout(() => {
            window.dispatchEvent(new CustomEvent('stats-refresh'))
          }, 300)
        }, 500)
      }
      
      // 自动处理完成通知（全自动模式）
      if (data.type === 'auto_process_complete') {
        // 使用 localStorage 协调多个标签页，确保只有一个标签页显示提示
        const lastShownTime = localStorage.getItem('auto_process_complete_last')
        const now = Date.now()
        
        // 如果1秒内已经显示过提示，跳过（说明其他标签页已经显示了）
        if (lastShownTime && (now - parseInt(lastShownTime)) < 1000) {
          // 跳过显示
        } else {
          // 记录显示时间
          localStorage.setItem('auto_process_complete_last', now.toString())
          // 1秒后清除记录
          setTimeout(() => {
            localStorage.removeItem('auto_process_complete_last')
          }, 1000)
          
          ElMessage.success(data.message)
        }
        // 刷新邮件列表（使用防抖机制）
        if (fetchTimer) {
          clearTimeout(fetchTimer)
        }
        fetchTimer = setTimeout(() => {
          fetchEmails(true)
          // 延迟通知其他页面刷新统计数据
          setTimeout(() => {
            window.dispatchEvent(new CustomEvent('stats-refresh'))
          }, 300)
        }, 500)
      }
      
      // 批量处理正在终止通知
      if (data.type === 'process_all_stopping') {
        // 设置正在终止状态
        isStoppingAll.value = true
        localStorage.setItem('is_stopping_all', 'true')  // 同步到 localStorage
        
        // 将所有 processing 状态的邮件设置为 stopping
        emails.value.forEach(email => {
          if (email.status === 'processing') {
            email.status = 'stopping'
            // processing 保持为 true
          }
        })
        
        // 如果当前选中的邮件也在处理中，也要更新
        if (selectedEmail.value && selectedEmail.value.status === 'processing') {
          selectedEmail.value.status = 'stopping'
        }
        
        console.log('[WebSocket] 批量处理正在终止:', data.count, '封邮件')
      }
      
      // 批量处理已终止通知
      if (data.type === 'process_all_stopped') {
        isProcessing.value = false
        isProcessingAll.value = false
        isStoppingAll.value = false  // 重置正在终止状态
        localStorage.removeItem('is_stopping_all')  // 清除 localStorage
        processAllStartTime.value = 0
        localStorage.removeItem('process_all_start_time')
        
        // 检查是否需要关闭自动处理
        const shouldCloseAutoProcess = localStorage.getItem('should_close_auto_process') === 'true'
        if (shouldCloseAutoProcess) {
          console.log('[终止完成] 关闭自动处理')
          localStorage.removeItem('should_close_auto_process')
          
          // 关闭自动处理
          settingsApi.getSettings().then(currentSettings => {
            settingsApi.saveSettings({
              ...currentSettings,
              autoProcess: false
            }).then(() => {
              systemStatus.value.autoProcess = false
              console.log('[终止完成] 已关闭自动处理')
            })
          })
        }
        
        ElMessage.info(data.message)
        
        // 刷新邮件列表
        if (fetchTimer) {
          clearTimeout(fetchTimer)
        }
        fetchTimer = setTimeout(() => {
          fetchEmails(true)
        }, 500)
      }
      
      // 单封邮件开始处理通知
      if (data.type === 'email_process_started') {
        const email = emails.value.find(e => e.id === data.email_id)
        if (email) {
          email.processing = true
          email.status = 'processing'
        }
        
        if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
          selectedEmail.value.processing = true
          selectedEmail.value.status = 'processing'
        }
        
        console.log('[WebSocket] 邮件开始处理:', data.email_id)
      }
      
      // 单封邮件正在终止通知
      if (data.type === 'email_process_stopping') {
        const email = emails.value.find(e => e.id === data.email_id)
        if (email) {
          email.status = 'stopping'
          // processing 保持为 true，让按钮继续显示禁用状态
        }
        
        if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
          selectedEmail.value.status = 'stopping'
          // processing 保持为 true
        }
        
        console.log('[WebSocket] 邮件正在终止:', data.email_id)
      }
      
      // 单封邮件处理已终止通知
      if (data.type === 'email_process_stopped') {
        const email = emails.value.find(e => e.id === data.email_id)
        if (email) {
          email.processing = false
          email.status = 'pending'
        }
        
        if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
          selectedEmail.value.processing = false
          selectedEmail.value.status = 'pending'
        }
        
        ElMessage.info(data.message)
        
        // 刷新邮件列表
        setTimeout(() => {
          fetchEmails(true)
        }, 500)
      }
      
      // RAG 查询问题生成通知
      if (data.type === 'rag_queries_generated') {
        console.log(`[RAG查询] 邮件 ${data.email_id} 生成了 ${data.count} 个查询问题:`, data.queries)
        
        // 找到对应的邮件，更新其 RAG 查询信息
        const email = emails.value.find(e => e.id === data.email_id)
        if (email) {
          email.rag_queries = data.queries
        }
        
        // 如果是当前选中的邮件，也更新
        if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
          selectedEmail.value.rag_queries = data.queries
          
          // 显示提示消息
          ElMessage.info({
            message: `已生成 ${data.count} 个知识库查询问题`,
            duration: 3000
          })
        }
      }
      
      // 单封邮件处理完成通知（手动点击"处理"按钮）
      if (data.type === 'email_process_complete') {
        // 首先检查是否在处理全部邮件的时间窗口内（必须在最开始检查）
        // 使用更严格的时间窗口判断（120秒，确保覆盖所有消息）
        const now = Date.now()
        const isInProcessAllWindow = isProcessingAll.value || 
          (processAllStartTime.value > 0 && now - processAllStartTime.value < 120000)
        
        // 如果正在处理全部邮件，直接跳过显示消息（但还是要更新邮件状态）
        if (isInProcessAllWindow) {
          console.log('[WebSocket消息处理] 跳过显示提示（正在处理全部邮件）:', {
            email_id: data.email_id,
            status: data.status,
            isProcessingAll: isProcessingAll.value,
            processAllStartTime: processAllStartTime.value,
            timeSinceStart: processAllStartTime.value > 0 ? now - processAllStartTime.value : 0
          })
          // 注意：即使不显示消息，也要更新邮件状态，所以不能直接 return
        }
        
        // 添加详细日志
        console.log('[WebSocket消息处理] 收到 email_process_complete 消息:', {
          email_id: data.email_id,
          status: data.status,
          category: data.category,
          message: data.message,
          timestamp: new Date().toISOString(),
          isProcessingAll: isProcessingAll.value,
          processAllStartTime: processAllStartTime.value,
          timeSinceStart: processAllStartTime.value > 0 ? now - processAllStartTime.value : 0,
          isInProcessAllWindow: isInProcessAllWindow,
          willShowMessage: !isInProcessAllWindow
        })
        
        // 防止重复处理同一条消息
        // 使用 email_id + status 作为唯一标识（更严格，防止同一条消息被多次处理）
        const messageKey = `${data.email_id}_${data.status}`
        
        // 先检查是否已经处理过这条消息（在添加记录之前检查，避免清理旧记录后再次处理）
        if (processedMessageIds.has(messageKey)) {
          console.log('[WebSocket消息处理] 忽略重复的 WebSocket 消息:', {
            messageKey,
            processedMessageIds: Array.from(processedMessageIds),
            reason: '消息已在处理记录中'
          })
          return
        }
        
        console.log('[WebSocket消息处理] 开始处理新消息:', {
          messageKey,
          currentProcessedCount: processedMessageIds.size
        })
        
        // 清理30秒前的旧记录（增加时间窗口，防止WebSocket重连后重复处理）
        const currentTime = Date.now()
        const keysToDelete = []
        for (const key of processedMessageIds) {
          // 如果键包含时间戳，检查是否过期
          const match = key.match(/_t(\d+)$/)
          if (match) {
            const keyTime = parseInt(match[1])
            if (currentTime - keyTime > 30000) { // 30秒
              keysToDelete.push(key)
            }
          } else {
            // 如果没有时间戳的旧格式键，也清理（兼容旧代码）
            keysToDelete.push(key)
          }
        }
        keysToDelete.forEach(key => processedMessageIds.delete(key))
        
        // 添加当前消息标识（使用简单的键，不包含时间戳，因为我们已经用时间戳清理旧记录）
        processedMessageIds.add(messageKey)
        console.log('[WebSocket消息处理] 已添加消息到处理记录:', {
          messageKey,
          totalProcessed: processedMessageIds.size,
          allKeys: Array.from(processedMessageIds)
        })
        
        // 30秒后清除，允许后续相同状态的消息（比如重试或重新处理）
        setTimeout(() => {
          processedMessageIds.delete(messageKey)
          console.log('[WebSocket消息处理] 已清除处理记录:', messageKey)
        }, 30000) // 30秒
        
        // 记录已完成的邮件状态（用于在刷新时强制更新）
        completedEmails.set(data.email_id, {
          status: data.status || 'processed',
          category: data.category,
          timestamp: Date.now()
        })
        // 5分钟后清除记录（避免内存泄漏）
        setTimeout(() => {
          completedEmails.delete(data.email_id)
        }, 5 * 60 * 1000)
        
        // 更新对应邮件的状态
        const email = emails.value.find(e => e.id === data.email_id)
        if (email) {
          // 立即更新状态，确保UI立即反映变化
          // 重要：必须重置 processing 标志，否则按钮会一直禁用
          email.processing = false
          email.status = data.status || 'processed'
          email.category = data.category || email.category
          
          console.log('[WebSocket消息处理] 已更新邮件状态:', {
            email_id: data.email_id,
            status: email.status,
            processing: email.processing,
            category: email.category
          })
          
          // 更新回复内容（如果WebSocket消息中包含reply字段）
          // 注意：即使reply是null或空字符串，也要更新，确保UI能正确显示
          if ('reply' in data) {
            email.reply = data.reply || null
            console.log('[WebSocket消息处理] 已更新邮件回复内容:', {
              email_id: data.email_id,
              has_reply: !!data.reply,
              reply_length: data.reply ? data.reply.length : 0
            })
          }
          
          // 更新紧急程度信息（如果WebSocket消息中包含相关字段）
          if (data.hasOwnProperty('urgency_level')) {
            email.urgency_level = data.urgency_level
            console.log('[WebSocket消息处理] 已更新邮件紧急程度:', {
              email_id: data.email_id,
              urgency_level: data.urgency_level
            })
          }
          
          if (data.hasOwnProperty('urgency_keywords')) {
            email.urgency_keywords = data.urgency_keywords || []
            console.log('[WebSocket消息处理] 已更新邮件紧急关键词:', {
              email_id: data.email_id,
              urgency_keywords: data.urgency_keywords
            })
          }
          
          // 更新 RAG 查询问题（如果WebSocket消息中包含相关字段）
          if (data.hasOwnProperty('rag_queries') && data.rag_queries) {
            email.rag_queries = data.rag_queries
            console.log('[WebSocket消息处理] 已更新 RAG 查询问题:', {
              email_id: data.email_id,
              rag_queries: data.rag_queries,
              count: data.rag_queries.length
            })
            
            // 如果是当前选中的邮件，同步更新可编辑的查询
            if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
              selectedEmail.value.rag_queries = data.rag_queries
              editableRagQueries.value = [...data.rag_queries]
            }
          }
          
          // 如果当前选中的邮件就是被处理的邮件，确保selectedEmail和email是同一个引用
          if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
            // 关键：直接使用email对象，确保引用一致
            // 这样更新email的属性时，selectedEmail也会自动更新
            selectedEmail.value = email
            
            // 重要：更新摘要状态，确保UI能正确显示回复内容
            if (email.status === 'processed' || email.status === 'sent' || email.status === 'skipped') {
              // 特殊处理：无关邮件的回复内容很短，直接显示，不需要摘要
              if (email.status === 'skipped') {
                emailSummary.reply = email.reply || ''
                emailSummary.replyStatus = 'ready'
                console.log('[WebSocket消息处理] 无关邮件，直接显示回复内容')
              } else if (email.reply_summary) {
                emailSummary.reply = email.reply_summary
                emailSummary.replyStatus = 'ready'
                console.log('[WebSocket消息处理] 已更新回复内容摘要（从 reply_summary）')
              } else if (email.reply) {
                // 如果没有摘要，使用简单截取作为临时预览
                const replyText = email.reply
                emailSummary.reply = replyText.length > 200 ? replyText.substring(0, 200) + '...' : replyText
                emailSummary.replyStatus = 'generating'
                console.log('[WebSocket消息处理] 已更新回复内容摘要（临时预览）')
              }
            }
          }
          
          // 显示处理结果（只显示一次）
          // 注意：如果正在处理全部邮件，不显示单封邮件的处理结果，避免重复提示
          // 使用 localStorage 协调多个标签页，确保只有一个标签页显示提示
          // 重要：这里再次检查 isInProcessAllWindow，确保在处理全部邮件时绝对不显示
          // 同时检查 localStorage 中是否有 process_all_start 标记（更可靠）
          const processAllStartMark = localStorage.getItem('process_all_start_time')
          const isInProcessAllWindowStrict = isInProcessAllWindow || 
            (processAllStartMark && Date.now() - parseInt(processAllStartMark) < 120000)
          
          if (!isInProcessAllWindowStrict) {
            const messageKey = `email_process_${data.email_id}_${data.status}`
            const lastShownTime = localStorage.getItem(messageKey)
            const showTime = Date.now()
            
            // 如果1秒内已经显示过相同的提示，跳过（说明其他标签页已经显示了）
            if (lastShownTime && (showTime - parseInt(lastShownTime)) < 1000) {
              console.log('[WebSocket消息处理] 跳过显示提示（其他标签页已显示）')
              return
            }
            
            // 记录显示时间
            localStorage.setItem(messageKey, showTime.toString())
            // 1秒后清除记录
            setTimeout(() => {
              localStorage.removeItem(messageKey)
            }, 1000)
            
            console.log('[WebSocket消息处理] 准备显示提示消息:', {
              status: data.status,
              message: data.message,
              isProcessingAll: isProcessingAll.value
            })
            
            if (data.status === 'skipped') {
              console.log('[WebSocket消息处理] 显示警告提示: 无关邮件，已跳过')
              ElMessage.warning(data.message || '无关邮件，已跳过')
            } else if (data.status === 'failed') {
              console.log('[WebSocket消息处理] 显示错误提示: 处理失败')
              ElMessage.error(data.message || '处理失败')
            } else {
              // 只显示简洁的成功消息，不显示"邮件已标记为已读"等详细信息
              const message = data.message || '处理成功'
              console.log('[WebSocket消息处理] 显示成功提示:', message)
              ElMessage.success(message)
            }
          } else {
            console.log('[WebSocket消息处理] 跳过显示提示（正在处理全部邮件）:', {
              isProcessingAll: isProcessingAll.value,
              processAllStartTime: processAllStartTime.value,
              timeSinceStart: processAllStartTime.value > 0 ? Date.now() - processAllStartTime.value : 0
            })
          }
        }
        
        // 注意：不要在这里重置 isProcessing，它只用于"处理全部邮件"
        // 单封邮件处理完成时，只重置该邮件的 processing 标志
        // isProcessing 应该只在"处理全部邮件"完成时重置（在 process_all_complete 消息处理中）
        
        // 刷新邮件列表（延迟一下，确保后端状态已更新）
        // 注意：不在这里显示任何消息，避免重复提示
        // 使用防抖机制，避免短时间内多次刷新
        if (fetchTimer) {
          clearTimeout(fetchTimer)
        }
        fetchTimer = setTimeout(() => {
          fetchEmails(true).then(() => {
            // 刷新后，再次确保状态正确（防止服务器返回旧状态）
            const refreshedEmail = emails.value.find(e => e.id === data.email_id)
            if (refreshedEmail) {
              // 强制更新状态，确保UI正确显示
              refreshedEmail.processing = false
              // 强制清除 processing 状态，无论服务器返回什么
              if (data.status && data.status !== 'processing') {
                refreshedEmail.status = data.status
              } else if (refreshedEmail.status === 'processing') {
                // 如果服务器返回的状态还是 processing（不应该发生），强制设置为 processed
                refreshedEmail.status = data.status || 'processed'
              }
              if (data.category) {
                refreshedEmail.category = data.category
              }
              // 如果WebSocket消息中包含reply字段，确保回复内容已更新
              if (data.hasOwnProperty('reply')) {
                refreshedEmail.reply = data.reply || null
              }
              
              // 如果当前选中的邮件就是被处理的邮件，也要同步更新 selectedEmail 的状态
              if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
                // 重新从 emails 数组中获取最新的邮件对象，确保引用一致
                selectedEmail.value = refreshedEmail
                // 再次确保状态正确
                selectedEmail.value.processing = false
                if (selectedEmail.value.status === 'processing') {
                  selectedEmail.value.status = data.status || 'processed'
                }
                // 确保回复内容已更新
                if (data.hasOwnProperty('reply')) {
                  selectedEmail.value.reply = data.reply || null
                }
              }
            } else {
              // 如果刷新后找不到邮件（可能被删除了），也要清除 selectedEmail 的状态
              if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
                selectedEmail.value.processing = false
                if (selectedEmail.value.status === 'processing') {
                  selectedEmail.value.status = data.status || 'processed'
                }
              }
            }
          }).catch(() => {
            // 即使刷新失败，也要确保本地状态正确
            const email = emails.value.find(e => e.id === data.email_id)
            if (email) {
              email.processing = false
              if (data.status) {
                email.status = data.status
              } else if (email.status === 'processing') {
                email.status = 'processed'
              }
              // 如果当前选中的邮件就是被处理的邮件，也要同步更新
              if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
                selectedEmail.value.processing = false
                if (data.status) {
                  selectedEmail.value.status = data.status
                } else if (selectedEmail.value.status === 'processing') {
                  selectedEmail.value.status = 'processed'
                }
              }
            }
          })
          // 延迟通知其他页面刷新统计数据，避免请求冲突
          setTimeout(() => {
            window.dispatchEvent(new CustomEvent('stats-refresh'))
          }, 500)
        }, 500) // 延迟500ms，合并多个WebSocket消息触发的刷新
      }
      
      // 摘要生成完成通知
      if (data.type === 'summary_saved') {
        console.log('[WebSocket消息处理] 收到 summary_saved 消息:', {
          email_id: data.email_id,
          has_body_summary: !!data.body_summary,
          has_reply_summary: !!data.reply_summary
        })
        
        // 更新对应邮件的摘要
        const email = emails.value.find(e => e.id === data.email_id)
        if (email) {
          if (data.body_summary) {
            email.body_summary = data.body_summary
          }
          if (data.reply_summary) {
            email.reply_summary = data.reply_summary
          }
          console.log('[WebSocket消息处理] 已更新邮件摘要:', {
            email_id: data.email_id,
            body_summary_length: data.body_summary ? data.body_summary.length : 0,
            reply_summary_length: data.reply_summary ? data.reply_summary.length : 0
          })
          
          // 如果当前选中的邮件就是这封邮件，也要更新 selectedEmail 和 emailSummary
          if (selectedEmail.value && selectedEmail.value.id === data.email_id) {
            if (data.body_summary) {
              selectedEmail.value.body_summary = data.body_summary
              emailSummary.body = data.body_summary
              emailSummary.bodyStatus = 'ready'
            }
            if (data.reply_summary) {
              selectedEmail.value.reply_summary = data.reply_summary
              emailSummary.reply = data.reply_summary
              emailSummary.replyStatus = 'ready'
            }
            console.log('[WebSocket消息处理] 已更新选中邮件的摘要，状态已设为 ready')
          }
        } else {
          console.log('[WebSocket消息处理] 未找到对应的邮件:', data.email_id)
        }
      }
    } catch (e) {
      console.error('解析 WebSocket 消息失败:', e)
    }
  }
  
  ws.onclose = () => {
    console.log('WebSocket 连接已断开，5秒后重连...')
    setTimeout(connectWebSocket, 5000)
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
  }
}

// 邮件数据
const emails = ref([])

// 防重复请求机制
let isFetching = false
let fetchTimer = null
let lastFetchTime = 0
const FETCH_DEBOUNCE_TIME = 300 // 300ms 内的重复请求会被忽略

// 标志：是否正在处理全部邮件（用于忽略刷新邮件的成功消息）
const isProcessingAll = ref(false)
// 标志：是否正在终止全部处理（主要由后端 WebSocket 通知控制，localStorage 作为备份）
const isStoppingAll = ref(localStorage.getItem('is_stopping_all') === 'true')
// 记录处理全部邮件的开始时间（用于判断单封邮件消息是否应该显示）
const processAllStartTime = ref(0)

// 记录已完成的邮件状态（用于在刷新时强制更新状态，防止服务器返回旧状态）
const completedEmails = new Map() // email_id -> { status, category, timestamp }

// 辅助函数：刷新邮件列表后，检查并更新已完成的邮件状态
const updateCompletedEmailStatus = () => {
  // 检查邮件列表中的已完成邮件
  emails.value.forEach(email => {
    const completedInfo = completedEmails.get(email.id)
    if (completedInfo) {
      // 如果服务器返回的状态还是 processing，强制更新为已完成状态
      if (email.status === 'processing' || email.processing) {
        email.processing = false
        email.status = completedInfo.status
        if (completedInfo.category) {
          email.category = completedInfo.category
        }
      }
    }
  })
  
  // 如果当前选中的邮件也需要更新
  if (selectedEmail.value) {
    const completedInfo = completedEmails.get(selectedEmail.value.id)
    if (completedInfo) {
      const refreshedEmail = emails.value.find(e => e.id === selectedEmail.value.id)
      if (refreshedEmail) {
        selectedEmail.value = refreshedEmail
      } else {
        // 如果邮件不在列表中，也要更新状态
        if (selectedEmail.value.status === 'processing' || selectedEmail.value.processing) {
          selectedEmail.value.processing = false
          selectedEmail.value.status = completedInfo.status
          if (completedInfo.category) {
            selectedEmail.value.category = completedInfo.category
          }
        }
      }
    }
  }
}

// 获取邮件列表（带防抖和防重复机制）
const fetchEmails = async (force = false) => {
  const now = Date.now()
  
  // 如果正在请求，检查是否需要等待
  if (isFetching) {
    // 如果是强制刷新，且距离上次请求超过防抖时间，允许执行
    if (force && (now - lastFetchTime > FETCH_DEBOUNCE_TIME)) {
      console.log('强制刷新，等待当前请求完成...')
      // 等待当前请求完成，但设置超时（最多等待3秒）
      let waitCount = 0
      const maxWait = 60 // 最多等待 60 * 50ms = 3秒
      while (isFetching && waitCount < maxWait) {
        await new Promise(resolve => setTimeout(resolve, 50))
        waitCount++
      }
      // 如果超时，强制重置状态
      if (isFetching) {
        console.warn('等待请求超时，强制重置状态')
        isFetching = false
        loading.value = false
      }
      // 继续执行下面的逻辑
    } else {
      console.log('邮件列表正在加载中，跳过重复请求')
      return
    }
  }
  
  // 检查是否在防抖时间内
  if (!force && (now - lastFetchTime < FETCH_DEBOUNCE_TIME)) {
    console.log('在防抖时间内，跳过重复请求')
    return
  }
  
  // 清除之前的定时器
  if (fetchTimer) {
    clearTimeout(fetchTimer)
    fetchTimer = null
  }
  
  // 如果是强制刷新，立即执行
  if (force) {
    isFetching = true
    loading.value = true
    lastFetchTime = now
    
    try {
      const res = await emailApi.getEmails({
        status: filterStatus.value,
        category: filterCategory.value
      })
      emails.value = res.emails || []
      updateCompletedEmailStatus() // 更新已完成的邮件状态
      
      // 如果邮件列表为空，自动触发一次刷新邮件操作（从QQ邮箱获取最新邮件）
      if (emails.value.length === 0) {
        console.log('邮件列表为空，自动刷新邮件...')
        try {
          await systemApi.refreshEmails()
          // 刷新后重新获取邮件列表
          const refreshRes = await emailApi.getEmails({
            status: filterStatus.value,
            category: filterCategory.value
          })
          emails.value = refreshRes.emails || []
          updateCompletedEmailStatus() // 再次更新已完成的邮件状态
        } catch (refreshError) {
          const errorMsg = refreshError.response?.data?.detail || refreshError.message
          // 如果是邮箱配置错误，不显示错误提示（避免干扰用户）
          if (!errorMsg || (!errorMsg.includes('未配置邮箱') && !errorMsg.includes('授权码'))) {
            console.warn('自动刷新邮件失败', refreshError)
          }
          // 刷新失败不影响，继续显示空列表
        }
      }
    } catch (e) {
      console.error('获取邮件失败', e)
      // API失败时显示空列表
      emails.value = []
    } finally {
      loading.value = false
      isFetching = false
    }
    return
  }
  
  // 防抖：延迟执行，如果短时间内多次调用，只执行最后一次
  fetchTimer = setTimeout(async () => {
    if (isFetching) {
      return
    }
    
    isFetching = true
    loading.value = true
    lastFetchTime = Date.now()
    
    try {
      const res = await emailApi.getEmails({
        status: filterStatus.value,
        category: filterCategory.value
      })
      emails.value = res.emails || []
      updateCompletedEmailStatus() // 更新已完成的邮件状态
      
      // 如果邮件列表为空，自动触发一次刷新邮件操作（从QQ邮箱获取最新邮件）
      if (emails.value.length === 0) {
        console.log('邮件列表为空，自动刷新邮件...')
        try {
          await systemApi.refreshEmails()
          // 刷新后重新获取邮件列表
          const refreshRes = await emailApi.getEmails({
            status: filterStatus.value,
            category: filterCategory.value
          })
          emails.value = refreshRes.emails || []
          updateCompletedEmailStatus() // 再次更新已完成的邮件状态
        } catch (refreshError) {
          const errorMsg = refreshError.response?.data?.detail || refreshError.message
          // 如果是邮箱配置错误，不显示错误提示（避免干扰用户）
          if (!errorMsg || (!errorMsg.includes('未配置邮箱') && !errorMsg.includes('授权码'))) {
            console.warn('自动刷新邮件失败', refreshError)
          }
          // 刷新失败不影响，继续显示空列表
        }
      }
    } catch (e) {
      console.error('获取邮件失败', e)
      // API失败时显示空列表
      emails.value = []
    } finally {
      loading.value = false
      isFetching = false
      fetchTimer = null
    }
  }, 100) // 100ms 防抖延迟
}

// 监听全局刷新事件（来自Layout.vue的刷新按钮）
const handleGlobalRefresh = (event) => {
  // 如果事件需要显示消息，显示成功消息
  // 但要注意：如果正在处理全部邮件，不显示刷新成功的消息（避免重复提示）
  if (event?.detail?.showMessage && !isProcessingAll.value) {
    // 延迟显示，避免与刷新操作冲突
    setTimeout(() => {
      ElMessage.success(event.detail?.message || '刷新完成')
    }, 100)
  }
  
  // 确保状态正确，然后强制刷新
  if (isFetching) {
    console.log('重置 isFetching 状态，准备重新获取邮件')
    isFetching = false
  }
  if (loading.value) {
    loading.value = false
  }
  fetchEmails(true) // 强制刷新
}

const route = useRoute()
const router = useRouter()
let isInitialized = false // 标记是否已初始化

// 当路由激活时（包括首次加载和从其他页面返回）自动加载邮件
onMounted(() => {
  if (!isInitialized) {
    // 首次加载时，从QQ邮箱同步最新状态，然后获取邮件列表（和刷新按钮逻辑一致）
    refreshEmailsFromServer(false) // 首次加载不显示消息
    isInitialized = true
  }
  // 获取系统状态（用于判断是否开启了自动处理）
  fetchSystemStatus()
  // 监听全局刷新事件
  window.addEventListener('emails-refresh', handleGlobalRefresh)
  // 建立 WebSocket 连接（如果还没有连接）
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    connectWebSocket()
  }
})

// 统一的刷新函数（从QQ邮箱同步最新状态，然后获取邮件列表）
let isRefreshing = false // 防止重复刷新
const refreshEmailsFromServer = async (showMessage = false) => {
  // 如果正在加载或正在刷新，不重复执行
  if (loading.value || isFetching || isRefreshing) {
    console.log('正在刷新中，跳过重复请求')
    return
  }
  
  isRefreshing = true
  loading.value = true
  isFetching = true
  
  try {
    // 调用系统刷新API，从QQ邮箱同步最新状态（和刷新按钮逻辑一致）
    const refreshRes = await systemApi.refreshEmails()
    // 刷新成功后，重新获取邮件列表（强制刷新）
    // 先重置状态，确保 fetchEmails 能正常执行
    if (isFetching) {
      console.log('重置 isFetching 状态，准备重新获取邮件')
      isFetching = false
    }
    // 重置 loading，因为 fetchEmails 会自己设置
    loading.value = false
    await fetchEmails(true)
    // 如果需要显示消息，显示成功消息（只有在处理全部邮件时不显示，避免重复提示）
    if (showMessage) {
      // 只有在不是处理全部邮件时才显示，避免在处理全部邮件时显示重复消息
      if (!isProcessingAll.value) {
        ElMessage.success(refreshRes?.message || '刷新完成')
      }
    }
  } catch (e) {
    console.error('刷新失败', e)
    // 优先使用 detail 字段（FastAPI 的错误信息），然后是 response.data.detail，最后是 message
    const errorMsg = e.detail || e.response?.data?.detail || e.message || '刷新失败'
    
    // 检查是否是邮箱配置错误
    if (errorMsg.includes('未配置邮箱') || errorMsg.includes('授权码') || errorMsg.includes('系统设置') || errorMsg.includes('尚未配置')) {
      ElMessageBox.alert(
        errorMsg + '<br/><br/>请前往【系统设置】页面完成邮箱配置。',
        '邮箱配置提示',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '前往设置',
          type: 'warning'
        }
      ).then(() => {
        // 跳转到系统设置页面
        router.push('/settings')
      })
    } else {
      // 路由跳转时的刷新失败，不显示错误消息（避免干扰用户），只记录日志
      console.warn('路由跳转时刷新邮件失败:', errorMsg)
    }
  } finally {
    loading.value = false
    isFetching = false
    isRefreshing = false
  }
}

// 使用 onActivated 确保从其他页面返回时也加载邮件（keep-alive场景）
onActivated(() => {
  // 只有在不是首次加载时才刷新
  if (isInitialized) {
    // 使用防抖，避免与 watch 同时触发
    if (fetchTimer) {
      clearTimeout(fetchTimer)
    }
    fetchTimer = setTimeout(() => {
      // 只获取邮件列表，不调用 refreshEmails（避免重复刷新）
      fetchEmails(true)
    }, 200)
  }
})

// 监听路由变化，当进入邮件管理页面时自动加载
watch(() => route.path, (newPath) => {
  if (newPath === '/emails' && isInitialized) {
    // 只有在已经初始化后才刷新，避免与 onMounted 重复
    // 使用防抖，避免与 onActivated 同时触发
    if (fetchTimer) {
      clearTimeout(fetchTimer)
    }
    fetchTimer = setTimeout(() => {
      // 只获取邮件列表，不调用 refreshEmails（避免重复刷新）
      fetchEmails(true)
    }, 200)
  }
})

onUnmounted(() => {
  // 移除事件监听
  window.removeEventListener('emails-refresh', handleGlobalRefresh)
  // 关闭 WebSocket 连接
  if (ws) {
    ws.close()
  }
})

// 待处理邮件
const pendingEmails = computed(() => {
  return emails.value.filter(e => e.status === 'pending')
})

// 是否有邮件正在处理（单个处理）
const hasProcessingEmails = computed(() => {
  return emails.value.some(e => e.status === 'processing' || e.status === 'stopping' || e.processing)
})

// 筛选后的邮件（不分页）
const filteredEmails = computed(() => {
  return emails.value.filter(email => {
    // 状态筛选
    if (filterStatus.value) {
      if (filterStatus.value === 'pending' && email.status !== 'pending') return false
      if (filterStatus.value === 'processed' && email.status === 'pending') return false
    }
    
    // 分类筛选（邮件获取时已自动分类）
    if (filterCategory.value && email.category !== filterCategory.value) {
      return false
    }
    
    // 关键词搜索
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      return (
        email.subject.toLowerCase().includes(keyword) ||
        email.sender.toLowerCase().includes(keyword) ||
        email.preview.toLowerCase().includes(keyword)
      )
    }
    
    return true
  })
})

// 分页后的邮件列表
const paginatedEmails = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEmails.value.slice(start, end)
})

// 分页变化处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1 // 改变每页数量时，重置到第一页
  // 保存到localStorage，以便刷新后恢复
  localStorage.setItem('email_page_size', val.toString())
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  // 滚动到顶部
  const emailListCard = document.querySelector('.email-list-card')
  if (emailListCard) {
    emailListCard.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 监听筛选条件变化，重置分页
watch([filterStatus, filterCategory, searchKeyword], () => {
  currentPage.value = 1
})

// 监听emails数组的变化，确保selectedEmail始终是最新的
watch(() => emails.value, (newEmails) => {
  // 如果当前有选中的邮件，从新的emails数组中获取最新的对象
  if (selectedEmail.value) {
    const latestEmail = newEmails.find(e => e.id === selectedEmail.value.id)
    if (latestEmail) {
      // 只有当对象引用不同时才更新，避免无限循环
      if (latestEmail !== selectedEmail.value) {
        selectedEmail.value = latestEmail
      }
    }
  }
}, { deep: true })

// 监听 selectedEmail.rag_queries 的变化，同步到可编辑的查询列表
watch(() => selectedEmail.value?.rag_queries, (newQueries, oldQueries) => {
  if (newQueries && newQueries.length > 0) {
    // 如果可编辑列表为空，或者数据是首次到达（从无到有），则同步
    if (editableRagQueries.value.length === 0 || !oldQueries || oldQueries.length === 0) {
      editableRagQueries.value = [...newQueries]
      console.log('[Watch] RAG查询问题已同步:', newQueries)
    }
  }
}, { deep: true, immediate: true })

// 分类映射
const getCategoryType = (category) => {
  const types = {
    'product_enquiry': 'primary',
    'customer_complaint': 'danger',
    'customer_feedback': 'success',
    'unrelated': 'info'
  }
  return types[category] || 'info'
}

const getCategoryLabel = (category) => {
  const labels = {
    'product_enquiry': '产品咨询',
    'customer_complaint': '客户投诉',
    'customer_feedback': '客户反馈',
    'unrelated': '无关邮件'
  }
  return labels[category] || category
}

// 紧急程度映射
const getUrgencyType = (urgency) => {
  const types = {
    'urgent': 'danger',
    'high': 'warning',
    'medium': 'primary',
    'low': 'info'
  }
  return types[urgency] || 'info'
}

const getUrgencyLabel = (urgency) => {
  const labels = {
    'urgent': '紧急',
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return labels[urgency] || urgency
}

// 选择邮件
const selectEmail = (email) => {
  console.log('[邮件详情] 选择邮件:', email)
  
  // 始终从emails数组中获取最新的邮件对象，确保引用一致
  const latestEmail = emails.value.find(e => e.id === email.id)
  selectedEmail.value = latestEmail || email
  
  // 同步可编辑的 RAG 查询问题
  if (selectedEmail.value.rag_queries && selectedEmail.value.rag_queries.length > 0) {
    editableRagQueries.value = [...selectedEmail.value.rag_queries]
  } else {
    editableRagQueries.value = []
  }
  
  // 重置展开状态
  showFullBody.value = false
  showFullReply.value = false
  
  // 检查邮件状态
  const isPending = selectedEmail.value.status === 'pending' || selectedEmail.value.status === 'processing'
  const isProcessed = selectedEmail.value.status === 'processed' || selectedEmail.value.status === 'sent' || selectedEmail.value.status === 'skipped'
  
  // 检查是否有摘要
  const hasBodySummary = selectedEmail.value.body_summary
  const hasReplySummary = selectedEmail.value.reply_summary
  
  console.log('[邮件详情] 邮件状态:', {
    status: selectedEmail.value.status,
    isPending,
    isProcessed,
    hasBodySummary,
    hasReplySummary,
    body_summary_length: hasBodySummary ? selectedEmail.value.body_summary.length : 0,
    reply_summary_length: hasReplySummary ? selectedEmail.value.reply_summary.length : 0
  })
  
  // 原始邮件摘要（所有邮件都显示）
  if (hasBodySummary) {
    emailSummary.body = selectedEmail.value.body_summary
    emailSummary.bodyStatus = 'ready'
    console.log('[邮件详情] 原始邮件摘要已存在')
  } else if (selectedEmail.value.body) {
    // 如果没有摘要，使用简单截取作为临时预览
    const bodyText = selectedEmail.value.body
    emailSummary.body = bodyText.length > 200 ? bodyText.substring(0, 200) + '...' : bodyText
    emailSummary.bodyStatus = 'generating'
    console.log('[邮件详情] 原始邮件摘要生成中')
  } else {
    emailSummary.body = ''
    emailSummary.bodyStatus = 'none'
  }
  
  // 回复内容摘要（只有已处理的邮件才显示）
  if (isProcessed) {
    // 特殊处理：无关邮件的回复内容很短，直接显示，不需要摘要
    if (selectedEmail.value.status === 'skipped') {
      emailSummary.reply = selectedEmail.value.reply || ''
      emailSummary.replyStatus = 'ready'
      console.log('[邮件详情] 无关邮件，直接显示回复内容')
    } else if (hasReplySummary) {
      emailSummary.reply = selectedEmail.value.reply_summary
      emailSummary.replyStatus = 'ready'
      console.log('[邮件详情] 回复内容摘要已存在')
    } else if (selectedEmail.value.reply) {
      // 如果没有摘要，使用简单截取作为临时预览
      const replyText = selectedEmail.value.reply
      emailSummary.reply = replyText.length > 200 ? replyText.substring(0, 200) + '...' : replyText
      emailSummary.replyStatus = 'generating'
      console.log('[邮件详情] 回复内容摘要生成中')
    } else {
      emailSummary.reply = ''
      emailSummary.replyStatus = 'none'
    }
  } else {
    // 未处理的邮件不显示回复内容摘要
    emailSummary.reply = ''
    emailSummary.replyStatus = 'none'
    console.log('[邮件详情] 未处理的邮件，不显示回复内容')
  }
}

// 切换展开/收起
const toggleFullContent = (type) => {
  if (type === 'body') {
    showFullBody.value = !showFullBody.value
  } else {
    showFullReply.value = !showFullReply.value
  }
}

// 刷新邮件（从QQ邮箱重新获取）
const handleRefresh = async () => {
  // 如果正在加载，不重复执行
  if (loading.value || isFetching) {
    return
  }
  
  loading.value = true
  isFetching = true
  
  try {
    // 调用系统刷新API，从QQ邮箱同步最新状态
    const refreshRes = await systemApi.refreshEmails()
    // 刷新成功后，重新获取邮件列表（强制刷新）
    await fetchEmails(true)
    // 刷新按钮总是显示成功消息（除非正在处理全部邮件，避免重复提示）
    if (!isProcessingAll.value) {
      ElMessage.success(refreshRes?.message || '刷新完成')
    }
  } catch (e) {
    console.error('刷新失败', e)
    // 优先使用 detail 字段（FastAPI 的错误信息），然后是 response.data.detail，最后是 message
    const errorMsg = e.detail || e.response?.data?.detail || e.message || '刷新失败'
    
    // 检查是否是邮箱配置错误
    if (errorMsg.includes('未配置邮箱') || errorMsg.includes('授权码') || errorMsg.includes('系统设置') || errorMsg.includes('尚未配置')) {
      ElMessageBox.alert(
        errorMsg + '<br/><br/>请前往【系统设置】页面完成邮箱配置。',
        '邮箱配置提示',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '前往设置',
          type: 'warning'
        }
      ).then(() => {
        // 跳转到系统设置页面
        router.push('/settings')
      })
    } else {
      ElMessage.error(errorMsg)
    }
  } finally {
    loading.value = false
    isFetching = false
  }
}

// 检查大模型配置（已移除API密钥检查，因为系统默认使用后端配置的API）
const checkAIConfig = async () => {
  try {
    const res = await settingsApi.getSettings()
    // 检查是否选择了模型（不再检查API密钥，因为系统默认模型使用后端配置的API）
    if (!res.replyModel && !res.model) {
      ElMessage.warning('请先选择回复大模型')
        router.push('/settings')
      return false
    }
    return true
  } catch (e) {
    console.error('检查大模型配置失败', e)
    // 如果获取设置失败，静默返回true（使用系统默认配置）
    return true
  }
}

// 处理全部
const handleProcessAll = async () => {
  // 先检查大模型配置
  const hasAIConfig = await checkAIConfig()
  if (!hasAIConfig) {
    return
  }
  
  ElMessageBox.confirm(
    `确定要AI处理全部 ${pendingEmails.value.length} 封待处理邮件吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    isProcessing.value = true
    isProcessingAll.value = true  // 设置标志，表示正在处理全部
    processAllStartTime.value = Date.now()  // 记录开始时间
    // 同时在 localStorage 中记录开始时间（用于跨标签页检查）
    localStorage.setItem('process_all_start_time', processAllStartTime.value.toString())
    ElMessage.info('AI正在处理全部邮件，请耐心等待...')
    try {
      await emailApi.processAllEmails()
      // 后端立即返回，实际处理在后台进行
      // 处理完成后会通过 WebSocket 通知并自动刷新
      // 这里不立即刷新，避免与 WebSocket 通知重复
      // 只刷新一次以显示处理中状态（延迟执行，避免立即重复）
      setTimeout(() => {
        fetchEmails(true)
      }, 500)
    } catch (e) {
      isProcessing.value = false
      isProcessingAll.value = false  // 处理失败时也要重置标志
      processAllStartTime.value = 0
      ElMessage.error('处理失败')
    }
    // 注意：不在这里重置 isProcessing，由 WebSocket 收到完成通知后重置
  }).catch(() => {
    // 用户取消时也要重置标志
    isProcessingAll.value = false
    processAllStartTime.value = 0
  })
}

// 处理单封邮件
const handleProcess = async (email) => {
  // 先检查大模型配置
  const hasAIConfig = await checkAIConfig()
  if (!hasAIConfig) {
    return
  }
  
  // 如果已经在处理中，不重复处理
  if (email.processing || email.status === 'processing') {
    ElMessage.warning('邮件正在处理中，请稍候')
    return
  }
  
  // 提示用户需要等待
  ElMessage.info('AI正在处理邮件，请耐心等待...')
  
  try {
    await emailApi.processEmail(email.id)
    
    // 后端会立即通过WebSocket发送 email_process_started 通知
    // 前端接收通知后会自动更新邮件状态为 processing
    // 处理完成后会通过 WebSocket 发送 email_process_complete 通知
    // 完全依赖WebSocket通知更新状态，不在这里手动设置
    console.log('邮件处理请求已发送，等待WebSocket通知更新状态...')
    
  } catch (e) {
    // 只有在API调用失败时才手动更新状态
    email.processing = false
    email.status = 'failed'
    const errorMsg = e.response?.data?.detail || e.message || '处理失败'
    ElMessage.error('处理失败: ' + errorMsg)
  }
}

// 标记已读
const handleMarkRead = async (email) => {
  try {
    await emailApi.markAsRead(email.id)
    email.status = 'read'
    ElMessage.success('已标记为已读')
    // 刷新邮件列表
    fetchEmails()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 重新检索（使用修改后的 RAG 查询问题）
const handleReRetrieve = async () => {
  if (!selectedEmail.value || !editableRagQueries.value.length) {
    ElMessage.warning('没有可用的查询问题')
    return
  }
  
  // 检查是否有空问题
  const emptyQueries = editableRagQueries.value.filter(q => !q.trim())
  if (emptyQueries.length > 0) {
    ElMessage.warning('请填写所有查询问题')
    return
  }
  
  isRetrieving.value = true
  
  try {
    const result = await emailApi.reRetrieve(selectedEmail.value.id, editableRagQueries.value)
    
    // 更新邮件的回复内容
    if (result.reply) {
      selectedEmail.value.reply = result.reply
      
      // 同步到邮件列表
      const email = emails.value.find(e => e.id === selectedEmail.value.id)
      if (email) {
        email.reply = result.reply
      }
    }
    
    // 更新 RAG 查询
    if (result.rag_queries) {
      selectedEmail.value.rag_queries = result.rag_queries
      editableRagQueries.value = [...result.rag_queries]
    }
    
    ElMessage.success('重新检索完成，回复已更新')
    
  } catch (error) {
    console.error('重新检索失败:', error)
    ElMessage.error('重新检索失败: ' + (error.message || '未知错误'))
  } finally {
    isRetrieving.value = false
  }
}

// 删除邮件
const handleDelete = async (email) => {
  ElMessageBox.confirm(
    `确定要删除这封邮件吗？\n主题：${email.subject}`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await emailApi.deleteEmail(email.id)
      ElMessage.success('邮件已删除')
      // 从列表中移除
      const index = emails.value.findIndex(e => e.id === email.id)
      if (index > -1) {
        emails.value.splice(index, 1)
      }
      // 通知其他页面刷新统计数据
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('stats-refresh'))
      }, 300)
    } catch (e) {
      const errorMsg = e.response?.data?.detail || e.message || '删除失败'
      ElMessage.error('删除失败: ' + errorMsg)
    }
  }).catch(() => {})
}

// 删除所有可删除的邮件（已处理、已跳过、处理失败的邮件）
const handleDeleteAll = async () => {
  // 统计可删除的邮件（已处理、已跳过、处理失败的邮件）
  const deletableEmails = emails.value.filter(e => 
    e.status === 'processed' || e.status === 'skipped' || e.status === 'failed'
  )
  const pendingEmails = emails.value.filter(e => 
    e.status === 'pending' || e.status === 'processing'
  )
  
  if (deletableEmails.length === 0) {
    ElMessage.warning('没有可删除的邮件（只有未处理的邮件）')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除所有已处理的邮件吗？\n将删除 ${deletableEmails.length} 封邮件（已处理/已跳过/处理失败）\n保留 ${pendingEmails.length} 封未处理邮件\n此操作不可恢复！`,
    '确认清空可删除邮件',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error',
      dangerouslyUseHTMLString: false
    }
  ).then(async () => {
    try {
      const res = await emailApi.deleteAllEmails()
      const deletedCount = res.count || deletableEmails.length
      const keptCount = res.kept || pendingEmails.length
      ElMessage.success(`已删除 ${deletedCount} 封可删除的邮件，保留 ${keptCount} 封未处理邮件`)
      // 刷新邮件列表
      await fetchEmails()
      // 如果当前选中的邮件被删除了，清空选中状态
      if (selectedEmail.value && (selectedEmail.value.status === 'processed' || selectedEmail.value.status === 'skipped' || selectedEmail.value.status === 'failed')) {
        selectedEmail.value = null
      }
      // 通知其他页面刷新统计数据
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('stats-refresh'))
      }, 300)
    } catch (e) {
      const errorMsg = e.response?.data?.detail || e.message || '删除失败'
      ElMessage.error('删除失败: ' + errorMsg)
    }
  }).catch(() => {})
}

// 发送回复
const handleSendReply = (email) => {
  ElMessageBox.confirm('确定要发送此回复吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      // 设置发送中状态
      email.sending = true
      
      await emailApi.sendReply(email.id, email.reply)
      ElMessage.success('回复已发送')
      
      // 更新邮件状态为已发送
      email.status = 'sent'
      email.sending = false
      
      // 刷新邮件列表
      fetchEmails()
      
      // 通知其他页面刷新统计数据
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('stats-refresh'))
      }, 500)
    } catch (e) {
      email.sending = false
      ElMessage.error('发送失败')
    }
  }).catch(() => {})
}

// 编辑回复
const handleEditReply = (email) => {
  editingReply.value = email.reply || ''
  editDialogVisible.value = true
}

// 保存回复（更新到后端）
const saveReply = async () => {
  if (selectedEmail.value) {
    try {
      // 调用后端API更新回复内容
      await emailApi.updateReply(selectedEmail.value.id, editingReply.value)
      // 更新前端显示
      selectedEmail.value.reply = editingReply.value
      editDialogVisible.value = false
      ElMessage.success('回复已保存')
    } catch (e) {
      console.error('保存回复失败', e)
      ElMessage.error('保存回复失败，请稍后重试')
    }
  }
}

// 终止全部处理（处理全部或自动处理）
const handleStopProcessing = async () => {
  // 判断是自动处理还是手动处理全部
  const isAutoProcess = systemStatus.value.autoProcess
  const confirmMessage = isAutoProcess 
    ? '确定要关闭自动处理吗？\n系统将停止自动处理新邮件，并终止所有正在处理的邮件。'
    : '确定要终止全部处理吗？\n系统将停止处理剩余邮件，正在处理的邮件将在下一个检查点终止。'
  
  try {
    await ElMessageBox.confirm(
      confirmMessage,
      '确认终止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 无论是自动处理还是手动处理全部，都调用终止API
    try {
      // 调用终止API（不要在这里设置 isStoppingAll，等待后端的 WebSocket 通知）
      await emailApi.stopProcessAll()
      
      // 注意：不要立即关闭 autoProcess，等待 WebSocket 通知终止完成后再关闭
      // 这样可以保持"正在终止全部..."按钮的显示
      // autoProcess 会在收到 process_all_stopped 消息时自动关闭（如果需要的话）
      
      // 如果是自动处理，记录需要关闭自动处理（延迟到终止完成后）
      if (isAutoProcess) {
        console.log('[终止] 自动处理模式，将在终止完成后关闭自动处理')
        // 设置一个标志，表示需要在终止完成后关闭自动处理
        localStorage.setItem('should_close_auto_process', 'true')
      }
      
      // 不再立即更新本地状态和显示成功消息
      // WebSocket会先发送 process_all_stopping 消息（显示"正在终止..."）
      // 然后每封邮件终止成功后发送 email_process_stopped 消息
      // 最后发送 process_all_stopped 消息（汇总）
      
    } catch (e) {
      console.error('终止处理失败', e)
      ElMessage.error('终止处理失败')
      return
    }
  } catch (e) {
    // 用户取消
  }
}

// 终止单封邮件处理
const handleStopSingleEmail = async (email) => {
  console.log('[终止] 点击终止按钮，邮件ID:', email.id, '状态:', email.status)
  
  try {
    await ElMessageBox.confirm(
      '确定要终止处理这封邮件吗？',
      '确认终止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    console.log('[终止] 用户确认终止，开始调用API')
    
    try {
      await emailApi.stopProcessEmail(email.id)
      
      console.log('[终止] API调用成功，等待WebSocket通知')
      
      // 不再立即更新本地状态，等待WebSocket通知
      // WebSocket会先发送 email_process_stopping 消息（显示"正在终止..."）
      // 然后在真正终止成功后发送 email_process_stopped 消息（更新为pending状态）
      
    } catch (e) {
      console.error('终止处理失败', e)
      ElMessage.error('终止处理失败')
    }
  } catch (e) {
    console.log('[终止] 用户取消终止')
  }
}
</script>

<style lang="scss" scoped>
.emails-page {
  background: var(--bg-color);
  transition: background-color 0.3s ease;
  
  .toolbar-card {
    margin-bottom: 20px;
    
    :deep(.el-card__body) {
      padding: 16px 20px;
    }
    
    .toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      
      .toolbar-left,
      .toolbar-right {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .email-list-card {
    .loading-container,
    .empty-container {
      padding: 40px 0;
      text-align: center;
      color: var(--text-secondary);
      
      .is-loading {
        animation: rotating 2s linear infinite;
      }
    }
    
    .email-list {
      .pagination-container {
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: center;
      }
      
      .email-item {
        display: flex;
        align-items: flex-start;
        padding: 16px;
        border-bottom: 1px solid var(--border-color);
        cursor: pointer;
        transition: background-color 0.2s;
        
        &:hover {
          background-color: var(--bg-color);
        }
        
        &.is-selected {
          background-color: rgba(64, 158, 255, 0.1);
        }
        
        &.is-unread {
          .email-subject {
            font-weight: 600;
          }
        }
        
        .email-status {
          margin-right: 12px;
          padding-top: 2px;
        }
        
        .email-content {
          flex: 1;
          min-width: 0;
          
          .email-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            
            .email-sender {
              font-size: 14px;
              color: var(--text-primary);
              font-weight: 500;
            }
            
            .email-time {
              font-size: 12px;
              color: var(--text-secondary);
            }
          }
          
          .email-subject {
            font-size: 14px;
            color: var(--text-primary);
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-weight: 500;
          }
          
          .email-preview {
            font-size: 12px;
            color: var(--text-secondary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-bottom: 8px;
          }
        }
        
        .email-actions {
          margin-left: 12px;
          display: flex;
          gap: 8px;
        }
      }
    }
  }
  
  .email-detail-card {
    position: sticky;
    top: 20px;
    
    .email-detail {
      .detail-header {
        .detail-subject {
          font-size: 18px;
          color: var(--text-primary);
          margin: 0 0 12px;
          font-weight: 600;
        }
        
        .detail-meta {
          display: flex;
          align-items: center;
          gap: 16px;
          flex-wrap: wrap;
          
          .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 14px;
            color: var(--text-regular);
          }
        }
      }
      
      .detail-section {
        margin-top: 20px;
        
        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          
          h4 {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: var(--text-primary);
            margin: 0;
            font-weight: 600;
          }
        }
        
        .summary-box {
          padding: 16px;
          background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(103, 194, 58, 0.05) 100%);
          border-radius: 8px;
          border: 1px solid rgba(64, 158, 255, 0.2);
          
          .summary-content {
            .summary-text {
              font-size: 14px;
              line-height: 1.8;
              color: var(--text-primary);
              white-space: pre-wrap;
            }
            
            .summary-loading {
              display: flex;
              align-items: center;
              gap: 8px;
              color: var(--text-secondary);
              font-size: 14px;
              
              .el-icon {
                font-size: 16px;
              }
            }
          }
          
          .summary-hint {
            margin-top: 12px;
            font-size: 12px;
            color: var(--text-secondary);
            text-align: center;
          }
        }
        
        .section-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .rag-queries-box {
          padding: 16px;
          background: linear-gradient(135deg, rgba(230, 162, 60, 0.05) 0%, rgba(64, 158, 255, 0.08) 100%);
          border-radius: 8px;
          border: 1px solid rgba(230, 162, 60, 0.3);
          
          .rag-query-item {
            margin: 12px 0;
            padding: 12px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #e6a23c;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            
            &.editable {
              border-left-color: #409eff;
              
              &:focus-within {
                box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
                border-left-color: #409eff;
              }
            }
            
            .query-number {
              font-size: 12px;
              color: #409eff;
              font-weight: 600;
              margin-bottom: 8px;
            }
            
            .query-content {
              font-size: 14px;
              line-height: 1.6;
              color: var(--text-primary);
              white-space: pre-wrap;
            }
            
            .query-input {
              :deep(.el-textarea__inner) {
                font-size: 14px;
                line-height: 1.6;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px 12px;
                
                &:focus {
                  border-color: #409eff;
                }
              }
            }
          }
        }
        
        .detail-body,
        .detail-reply {
          padding: 16px;
          background-color: var(--bg-color);
          border-radius: 8px;
          font-size: 14px;
          line-height: 1.8;
          color: var(--text-primary);
          white-space: pre-wrap;
          border: 1px solid var(--border-color);
        }
        
        .detail-reply {
          background-color: rgba(103, 194, 58, 0.1);
          border-color: rgba(103, 194, 58, 0.3);
        }
      }
      
      .detail-actions {
        margin-top: 20px;
        display: flex;
        gap: 12px;
      }
    }
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>