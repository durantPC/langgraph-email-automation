<template>
  <div class="history-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>处理记录</span>
          <el-button type="primary" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出XLSX
          </el-button>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-bar">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          format="YYYY-MM-DD"
        />
        <el-select v-model="filterCategory" placeholder="分类" clearable>
          <el-option label="全部" value="" />
          <el-option label="产品咨询" value="product_enquiry" />
          <el-option label="客户投诉" value="customer_complaint" />
          <el-option label="客户反馈" value="customer_feedback" />
          <el-option label="无关邮件" value="unrelated" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable>
          <el-option label="全部" value="" />
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="跳过" value="skipped" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
      </div>
      
      <!-- 记录表格 -->
      <el-table :data="records" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="time" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.time || row.processed_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="sender" label="发件人" width="200" show-overflow-tooltip />
        <el-table-column prop="subject" label="主题" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="showDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="处理详情" width="600px" @close="handleDialogClose">
      <div v-if="currentRecord" class="detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="时间">{{ formatTime(currentRecord.time || currentRecord.processed_time) }}</el-descriptions-item>
          <el-descriptions-item label="发件人">{{ currentRecord.sender || currentRecord.sender_email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="主题">{{ currentRecord.subject || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag :type="getCategoryType(currentRecord.category)" size="small">
              {{ getCategoryLabel(currentRecord.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentRecord.status)" size="small">
              {{ getStatusLabel(currentRecord.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentRecord.body || currentRecord.content" class="detail-section">
          <div class="section-header">
            <h4>原始邮件</h4>
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
              <div class="summary-text" v-if="summary.body">
                {{ summary.body }}
              </div>
              <div v-else class="summary-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在生成摘要...</span>
              </div>
            </div>
            <div class="summary-hint">点击"展开全文"查看完整内容</div>
          </div>
          <div v-show="showFullBody" class="detail-body">
            {{ currentRecord.body || currentRecord.content || '-' }}
          </div>
        </div>
        
        <div v-if="currentRecord.reply" class="detail-section">
          <div class="section-header">
            <h4>回复内容</h4>
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
              <div class="summary-text" v-if="summary.reply">
                {{ summary.reply }}
              </div>
              <div v-else class="summary-loading">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在生成摘要...</span>
              </div>
            </div>
            <div class="summary-hint">点击"展开全文"查看完整内容</div>
          </div>
          <div v-show="showFullReply" class="detail-reply">
            {{ currentRecord.reply }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search, Loading, Clock } from '@element-plus/icons-vue'
import { historyApi } from '@/api'

const dateRange = ref([])
const filterCategory = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
// 从localStorage读取保存的每页数量
const pageSize = ref(parseInt(localStorage.getItem('history_page_size') || '10', 10))
const total = ref(0)
const detailVisible = ref(false)
const currentRecord = ref(null)
const records = ref([])
const loading = ref(false)

// 摘要相关状态
const showFullBody = ref(false)
const showFullReply = ref(false)
const summary = reactive({
  body: '',
  reply: '',
  bodyStatus: 'none',  // 'none' | 'generating' | 'ready'
  replyStatus: 'none'  // 'none' | 'generating' | 'ready'
})

// 轮询相关
let summaryCheckInterval = null
let summaryCheckErrorCount = 0
const MAX_SUMMARY_CHECK_ERRORS = 5

// 获取处理记录
const fetchRecords = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 添加筛选条件
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    if (filterCategory.value) {
      params.category = filterCategory.value
    }
    
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    
    const res = await historyApi.getHistory(params)
    console.log('获取处理记录响应:', res) // 调试日志
    if (res && res.records) {
      records.value = res.records || []
      total.value = res.total || 0
    } else {
      records.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取处理记录失败:', error)
    ElMessage.error('获取处理记录失败')
    records.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const getCategoryType = (category) => {
  const types = { 'product_enquiry': 'primary', 'customer_complaint': 'danger', 'customer_feedback': 'success', 'unrelated': 'info' }
  return types[category] || 'info'
}

const getCategoryLabel = (category) => {
  const labels = { 'product_enquiry': '产品咨询', 'customer_complaint': '客户投诉', 'customer_feedback': '客户反馈', 'unrelated': '无关邮件' }
  return labels[category] || '-'
}

const getStatusType = (status) => {
  // 状态映射：success/processed/sent -> success, failed -> danger, skipped -> info
  if (status === 'success' || status === 'processed' || status === 'sent') {
    return 'success'
  } else if (status === 'failed') {
    return 'danger'
  } else if (status === 'skipped') {
    return 'info'
  }
  return 'info'
}

const getStatusLabel = (status) => {
  // 状态映射：success/processed/sent -> 成功, failed -> 失败, skipped -> 跳过
  if (status === 'success' || status === 'processed' || status === 'sent') {
    return '成功'
  } else if (status === 'failed') {
    return '失败'
  } else if (status === 'skipped') {
    return '跳过'
  }
  return status || '未知'
}

const handleSearch = () => {
  currentPage.value = 1 // 重置到第一页
  fetchRecords()
}

const handleExport = async () => {
  try {
    const params = {}
    
    // 添加筛选条件
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    if (filterCategory.value) {
      params.category = filterCategory.value
    }
    
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    
    const res = await historyApi.exportHistory(params)
    console.log('导出响应类型:', typeof res, res instanceof Blob) // 调试日志
    
    // 当 responseType 为 'blob' 时，响应拦截器返回的 response.data 就是 blob 对象
    // 所以 res 本身就是 Blob，不需要再访问 res.data
    const blob = res instanceof Blob ? res : new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `处理记录_${new Date().toISOString().split('T')[0]}.xlsx`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  // 保存到localStorage，以便刷新后恢复
  localStorage.setItem('history_page_size', val.toString())
  fetchRecords()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchRecords()
}

// 格式化时间显示
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  try {
    const date = new Date(timeStr.replace(/-/g, '/'))
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  } catch (e) {
    return timeStr
  }
}

const showDetail = (row) => {
  console.log('[详情对话框] 打开详情对话框，记录:', row)
  
  currentRecord.value = row
  detailVisible.value = true
  
  // 重置展开状态
  showFullBody.value = false
  showFullReply.value = false
  
  // 检查是否有摘要
  const hasBodySummary = row.body_summary
  const hasReplySummary = row.reply_summary
  
  console.log('[详情对话框] 摘要状态:', {
    hasBodySummary,
    hasReplySummary,
    body_summary_length: hasBodySummary ? row.body_summary.length : 0,
    reply_summary_length: hasReplySummary ? row.reply_summary.length : 0
  })
  
  // 原始邮件摘要
  if (hasBodySummary) {
    summary.body = row.body_summary
    summary.bodyStatus = 'ready'  // 已生成
    console.log('[详情对话框] 原始邮件摘要已存在，长度:', row.body_summary.length)
  } else if (row.body || row.content) {
    // 如果没有摘要，使用简单截取作为临时预览
    const bodyText = row.body || row.content
    summary.body = bodyText.length > 200 ? bodyText.substring(0, 200) + '...' : bodyText
    summary.bodyStatus = 'generating'  // 生成中
    console.log('[详情对话框] 原始邮件摘要生成中，显示临时预览')
  } else {
    // 既没有摘要也没有原始内容
    summary.body = ''
    summary.bodyStatus = 'none'
  }
  
  // 回复内容摘要
  // 特殊处理：无关邮件的回复内容很短，直接显示，不需要摘要
  if (row.status === 'skipped') {
    summary.reply = row.reply || ''
    summary.replyStatus = 'ready'
    console.log('[详情对话框] 无关邮件，直接显示回复内容')
  } else if (hasReplySummary) {
    summary.reply = row.reply_summary
    summary.replyStatus = 'ready'  // 已生成
    console.log('[详情对话框] 回复内容摘要已存在，长度:', row.reply_summary.length)
  } else if (row.reply) {
    // 如果没有摘要，使用简单截取作为临时预览
    summary.reply = row.reply.length > 200 ? row.reply.substring(0, 200) + '...' : row.reply
    summary.replyStatus = 'generating'  // 生成中
    console.log('[详情对话框] 回复内容摘要生成中，显示临时预览')
  } else {
    // 既没有摘要也没有回复内容
    summary.reply = ''
    summary.replyStatus = 'none'
  }
  
  // 如果有任何摘要正在生成，启动轮询
  const needsPolling = summary.bodyStatus === 'generating' || summary.replyStatus === 'generating'
  
  console.log('[详情对话框] 是否需要轮询:', needsPolling, {
    bodyStatus: summary.bodyStatus,
    replyStatus: summary.replyStatus
  })
  
  if (needsPolling) {
    // 清除之前的轮询（如果有）
    if (summaryCheckInterval) {
      clearInterval(summaryCheckInterval)
      summaryCheckInterval = null
    }
    
    // 启动新的轮询
    summaryCheckErrorCount = 0
    summaryCheckInterval = setInterval(checkSummaryStatus, 3000)  // 每3秒检查一次
    console.log('[详情对话框] 已启动摘要轮询')
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

// 检查摘要是否已生成（轮询）
const checkSummaryStatus = async () => {
  if (!currentRecord.value || !currentRecord.value.id) {
    // 如果记录不存在，停止轮询
    if (summaryCheckInterval) {
      clearInterval(summaryCheckInterval)
      summaryCheckInterval = null
    }
    return
  }
  
  try {
    // 重新获取最近记录
    const res = await historyApi.getHistory({ page: 1, page_size: 20 })
    
    if (!res || !res.records) {
      console.warn('[摘要检查] 获取记录失败')
      summaryCheckErrorCount++
      if (summaryCheckErrorCount >= MAX_SUMMARY_CHECK_ERRORS) {
        console.warn('[摘要检查] 错误次数过多，停止轮询')
        if (summaryCheckInterval) {
          clearInterval(summaryCheckInterval)
          summaryCheckInterval = null
        }
      }
      return
    }
    
    const updatedRecord = res.records.find(r => r.id === currentRecord.value.id)
    
    if (updatedRecord) {
      // 重置错误计数
      summaryCheckErrorCount = 0
      
      // 如果原始邮件摘要已生成
      if (updatedRecord.body_summary && summary.bodyStatus === 'generating') {
        summary.body = updatedRecord.body_summary
        summary.bodyStatus = 'ready'
        console.log('[摘要检查] 原始邮件摘要已生成')
      }
      
      // 如果回复内容摘要已生成
      if (updatedRecord.reply_summary && summary.replyStatus === 'generating') {
        summary.reply = updatedRecord.reply_summary
        summary.replyStatus = 'ready'
        console.log('[摘要检查] 回复内容摘要已生成')
      }
      
      // 同步更新 records 列表中的数据
      const listRecord = records.value.find(r => r.id === currentRecord.value.id)
      if (listRecord) {
        if (updatedRecord.body_summary) {
          listRecord.body_summary = updatedRecord.body_summary
          console.log('[摘要检查] 已同步原始邮件摘要到列表')
        }
        if (updatedRecord.reply_summary) {
          listRecord.reply_summary = updatedRecord.reply_summary
          console.log('[摘要检查] 已同步回复内容摘要到列表')
        }
      }
      
      // 如果两个摘要都生成完成，停止轮询
      if (summary.bodyStatus !== 'generating' && summary.replyStatus !== 'generating') {
        if (summaryCheckInterval) {
          clearInterval(summaryCheckInterval)
          summaryCheckInterval = null
          console.log('[摘要检查] 所有摘要已生成，停止轮询')
        }
      }
    } else {
      // 如果找不到记录，可能是记录已被删除或不在最近20条中
      console.warn('[摘要检查] 未找到对应记录')
      summaryCheckErrorCount++
      if (summaryCheckErrorCount >= MAX_SUMMARY_CHECK_ERRORS) {
        console.warn('[摘要检查] 错误次数过多，停止轮询')
        if (summaryCheckInterval) {
          clearInterval(summaryCheckInterval)
          summaryCheckInterval = null
        }
      }
    }
  } catch (e) {
    summaryCheckErrorCount++
    console.error('[摘要检查] 检查摘要失败:', e)
    
    // 如果错误次数过多，停止轮询
    if (summaryCheckErrorCount >= MAX_SUMMARY_CHECK_ERRORS) {
      console.warn('[摘要检查] 错误次数过多，停止轮询')
      if (summaryCheckInterval) {
        clearInterval(summaryCheckInterval)
        summaryCheckInterval = null
      }
    }
  }
}

// 对话框关闭时清理轮询
const handleDialogClose = () => {
  if (summaryCheckInterval) {
    clearInterval(summaryCheckInterval)
    summaryCheckInterval = null
    console.log('[详情对话框] 对话框关闭，已停止轮询')
  }
}

// 初始化加载数据
onMounted(() => {
  fetchRecords()
})

// 组件卸载时清理轮询
onUnmounted(() => {
  if (summaryCheckInterval) {
    clearInterval(summaryCheckInterval)
    summaryCheckInterval = null
    console.log('[History] 组件卸载，已清理轮询')
  }
})

// 监听筛选条件变化，自动查询（可选，如果不需要自动查询可以删除）
// watch([dateRange, filterCategory, filterStatus], () => {
//   if (currentPage.value === 1) {
//     fetchRecords()
//   }
// })
</script>

<style lang="scss" scoped>
.history-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .detail-content {
    .detail-section {
      margin-top: 20px;
      
      .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        
        h4 {
          font-size: 14px;
          color: var(--text-primary);
          margin: 0;
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
      
      .detail-body,
      .detail-reply {
        padding: 16px;
        background-color: var(--bg-color);
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.8;
        white-space: pre-wrap;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
      }
      
      .detail-reply {
        background-color: rgba(103, 194, 58, 0.1);
        border-color: rgba(103, 194, 58, 0.3);
      }
    }
  }
}
</style>

