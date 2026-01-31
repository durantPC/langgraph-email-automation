<template>
  <div class="dashboard">
    <!-- AI助教入口模块 -->
    <AiAssistantEntry />
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-card-primary">
          <div class="stat-icon">
            <el-icon :size="28"><Message /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todayEmails }}</div>
            <div class="stat-label">今日邮件</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-card-success">
          <div class="stat-icon">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.processed }}</div>
            <div class="stat-label">已处理</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-card-warning">
          <div class="stat-icon">
            <el-icon :size="28"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card stat-card-danger">
          <div class="stat-icon">
            <el-icon :size="28"><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.failed }}</div>
            <div class="stat-label">处理失败</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>邮件分类统计</span>
              <el-tag size="small" type="info">今日</el-tag>
            </div>
          </template>
          <div class="chart-container" ref="categoryChartRef"></div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>近7天处理趋势</span>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近处理记录 -->
    <el-card shadow="hover" class="recent-card">
      <template #header>
        <div class="card-header">
          <span>最近处理的邮件</span>
          <el-button type="primary" link @click="$router.push('/history')">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      
      <el-table :data="recentEmails" stripe style="width: 100%">
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="主题" show-overflow-tooltip />
        <el-table-column prop="sender" label="发件人" width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <div class="status-icon-wrapper">
              <el-icon v-if="row.status === 'success'" color="#67c23a" :size="18"><CircleCheck /></el-icon>
              <el-icon v-else-if="row.status === 'failed'" color="#f56c6c" :size="18"><CircleClose /></el-icon>
              <el-icon v-else color="#e6a23c" :size="18"><Clock /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 空状态 -->
      <el-empty v-if="recentEmails.length === 0" description="暂无处理记录" />
      
      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="pagination.total > 0">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
    
    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="处理详情" width="600px">
      <div v-if="currentRecord" class="detail-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="时间">{{ formatTime(currentRecord.rawRecord?.time || currentRecord.rawRecord?.processed_time || '') }}</el-descriptions-item>
          <el-descriptions-item label="发件人">{{ currentRecord.sender }}</el-descriptions-item>
          <el-descriptions-item label="主题">{{ currentRecord.subject }}</el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag :type="getCategoryType(currentRecord.category)" size="small">
              {{ getCategoryLabel(currentRecord.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <div class="status-display">
              <el-icon v-if="currentRecord.status === 'success'" color="#67c23a" :size="18"><CircleCheck /></el-icon>
              <el-icon v-else-if="currentRecord.status === 'failed'" color="#f56c6c" :size="18"><CircleClose /></el-icon>
              <el-icon v-else color="#e6a23c" :size="18"><Clock /></el-icon>
              <span class="status-text">
                {{ currentRecord.status === 'success' ? '成功' : currentRecord.status === 'failed' ? '失败' : '待处理' }}
              </span>
            </div>
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentRecord.rawRecord?.body" class="detail-section">
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
            {{ currentRecord?.rawRecord?.body || '' }}
          </div>
        </div>
        
        <div v-if="currentRecord.rawRecord?.reply" class="detail-section">
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
            {{ currentRecord?.rawRecord?.reply || '' }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, onActivated, watch } from 'vue'
import * as echarts from 'echarts'
import { statsApi, historyApi, emailApi } from '@/api'
import {
  Message, CircleCheck, Clock, CircleClose, ArrowRight, Loading
} from '@element-plus/icons-vue'
import AiAssistantEntry from '@/components/ai/AiAssistantEntry.vue'

// 统计数据
const stats = reactive({
  todayEmails: 0,
  processed: 0,
  pending: 0,
  failed: 0
})

// 最近邮件
const recentEmails = ref([])

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 5,
  total: 0
})

// 详情对话框
const detailVisible = ref(false)
const currentRecord = ref(null)

// 获取统计数据 - 从后端获取真实数据，确保用户隔离
const fetchStats = async () => {
  try {
    const res = await statsApi.getStats()
    if (res) {
      stats.todayEmails = res.todayEmails || 0
      stats.processed = res.processed || 0
      stats.pending = res.pending || 0
      stats.failed = res.failed || 0
    }
  } catch (e) {
    console.error('获取统计数据失败', e)
    // 失败时保持当前值，不清零（避免处理邮件时统计数据被清零）
    // 只有在确实是网络错误或服务器错误时才考虑清零
    if (e.response?.status === 500 || !e.response) {
      // 服务器错误或网络错误，保持当前值
      console.warn('获取统计数据失败，保持当前值')
    }
    // 其他错误（如401、403）也保持当前值，不清零
  }
}

// 获取最近记录 - 从后端获取真实数据，确保用户隔离
const fetchRecentEmails = async () => {
  try {
    const res = await historyApi.getHistory({ 
      page: pagination.currentPage, 
      page_size: pagination.pageSize 
    })
    console.log('[Dashboard] 获取历史记录响应:', res)
    // 更新总数
    if (res && res.total !== undefined) {
      pagination.total = res.total
    }
    if (res && res.records && res.records.length > 0) {
      // 调试：检查第一条记录是否有摘要
      const firstRecord = res.records[0]
      console.log('[Dashboard] 第一条记录:', {
        id: firstRecord.id,
        subject: firstRecord.subject,
        has_body_summary: !!firstRecord.body_summary,
        has_reply_summary: !!firstRecord.reply_summary,
        body_summary_length: firstRecord.body_summary ? firstRecord.body_summary.length : 0,
        reply_summary_length: firstRecord.reply_summary ? firstRecord.reply_summary.length : 0
      })
      
      // 格式化时间显示并处理数据
      recentEmails.value = res.records.map(record => {
        // 处理发件人显示：提取姓名和邮箱
        let senderDisplay = record.sender || '未知发件人'
        if (senderDisplay.includes('<') && senderDisplay.includes('>')) {
          // 格式："姓名"<email@qq.com> -> 显示为 "姓名"<email...
          const match = senderDisplay.match(/^"([^"]+)"<([^>]+)>$/)
          if (match) {
            const name = match[1]
            const email = match[2]
            // 如果邮箱太长，截断显示
            const emailDisplay = email.length > 20 ? email.substring(0, 20) + '...' : email
            senderDisplay = `"${name}"<${emailDisplay}`
          }
        }
        
        return {
          id: record.id || '',
          time: formatTime(record.time || record.processed_time || ''),
          category: record.category || 'unknown',
          subject: record.subject || '无主题',
          sender: senderDisplay,
          status: record.status === 'success' || record.status === 'processed' || record.status === 'sent' ? 'success' : 
                  record.status === 'failed' ? 'failed' : 'pending',
          // 保存原始记录数据，用于详情查看
          rawRecord: record
        }
      })
    } else {
      recentEmails.value = []
    }
  } catch (e) {
    console.error('获取最近记录失败', e)
    // 失败时保持空数组，不使用默认数据
    recentEmails.value = []
  }
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

// 图表引用
const categoryChartRef = ref(null)
const trendChartRef = ref(null)
let categoryChart = null
let trendChart = null

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

// 获取分类统计数据并更新饼图
const fetchCategoryStats = async () => {
  try {
    const res = await statsApi.getCategoryStats()
    if (res && res.categories) {
      updateCategoryChart(res.categories)
    } else {
      updateCategoryChart({})
    }
  } catch (e) {
    console.error('获取分类统计失败', e)
    updateCategoryChart({})
  }
}

// 更新分类饼图
const updateCategoryChart = (categories) => {
  if (!categoryChartRef.value) return
  
  if (!categoryChart) {
    categoryChart = echarts.init(categoryChartRef.value)
  }
  
  // 分类映射
  const categoryMap = {
    'product_enquiry': { name: '产品咨询', color: '#409eff' },
    'customer_complaint': { name: '客户投诉', color: '#f56c6c' },
    'customer_feedback': { name: '客户反馈', color: '#67c23a' },
    'unrelated': { name: '无关邮件', color: '#909399' }
  }
  
  // 构建图表数据
  const chartData = []
  for (const [key, value] of Object.entries(categories)) {
    if (categoryMap[key]) {
      chartData.push({
        value: value,
        name: categoryMap[key].name,
        itemStyle: { color: categoryMap[key].color }
      })
    }
  }
  
  // 如果没有数据，显示空状态
  if (chartData.length === 0) {
    chartData.push({
      value: 0,
      name: '暂无数据',
      itemStyle: { color: '#909399' }
    })
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center'
    },
    series: [
      {
        name: '邮件分类',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: chartData
      }
    ]
  }
  
  categoryChart.setOption(option)
}

// 初始化分类饼图（仅创建实例，数据通过fetchCategoryStats获取）
const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)
  // 数据通过fetchCategoryStats获取
  fetchCategoryStats()
}

// 获取趋势数据并更新折线图
const fetchTrendStats = async () => {
  try {
    const res = await statsApi.getTrendStats(7)
    if (res && res.trend) {
      updateTrendChart(res.trend)
    } else {
      updateTrendChart([])
    }
  } catch (e) {
    console.error('获取趋势数据失败', e)
    updateTrendChart([])
  }
}

// 更新趋势折线图
const updateTrendChart = (trendData) => {
  if (!trendChartRef.value) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  // 提取日期和数值
  const dates = trendData.map(item => item.date || '')
  const receivedData = trendData.map(item => item.received || 0)
  const processedData = trendData.map(item => item.processed || 0)
  
  // 检测是否为深色模式
  const isDarkMode = document.documentElement.classList.contains('theme-dark')
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: isDarkMode ? 'rgba(30, 30, 30, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.2)',
      textStyle: {
        color: isDarkMode ? '#e5eaf3' : '#333'
      }
    },
    legend: {
      data: ['收到邮件', '已处理'],
      top: 0,
      textStyle: {
        color: isDarkMode ? '#e5eaf3' : '#333',
        fontSize: 14,
        fontWeight: 500
      },
      itemGap: 20
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates.length > 0 ? dates : ['暂无数据'],
      axisLabel: {
        color: isDarkMode ? '#a8abb2' : '#606266'
      },
      axisLine: {
        lineStyle: {
          color: isDarkMode ? '#4c4d4f' : '#dcdfe6'
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: isDarkMode ? '#a8abb2' : '#606266'
      },
      axisLine: {
        lineStyle: {
          color: isDarkMode ? '#4c4d4f' : '#dcdfe6'
        }
      },
      splitLine: {
        lineStyle: {
          color: isDarkMode ? '#4c4d4f' : '#e4e7ed'
        }
      }
    },
    series: [
      {
        name: '收到邮件',
        type: 'line',
        smooth: true,
        areaStyle: {
          opacity: 0.3
        },
        data: receivedData.length > 0 ? receivedData : [0],
        itemStyle: { color: '#409eff' }
      },
      {
        name: '已处理',
        type: 'line',
        smooth: true,
        areaStyle: {
          opacity: 0.3
        },
        data: processedData.length > 0 ? processedData : [0],
        itemStyle: { color: '#67c23a' }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 初始化趋势折线图（仅创建实例，数据通过fetchTrendStats获取）
const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  // 数据通过fetchTrendStats获取
  fetchTrendStats()
}

// 展开/收起状态
const showFullBody = ref(false)
const showFullReply = ref(false)

// 摘要内容
const summary = reactive({
  body: '',
  reply: '',
  bodyStatus: '',  // 'ready' 已生成, 'generating' 生成中, '' 无内容
  replyStatus: ''  // 'ready' 已生成, 'generating' 生成中, '' 无内容
})

// 轮询检查摘要的定时器
let summaryCheckInterval = null

// WebSocket 连接（用于推送摘要已生成通知）
let ws = null
const connectWebSocket = () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = window.location.hostname || 'localhost'
    const port = window.location.port || '8000'
    const wsUrl = `${protocol}://${host}:${port}/api/ws?token=${encodeURIComponent(token)}`
    ws = new WebSocket(wsUrl)
    ws.onopen = () => {
      console.log('[WS] 已连接到服务器')
    }
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg && msg.type === 'summary_saved') {
          console.log('[WS] 收到 summary_saved 消息:', {
            email_id: msg.email_id,
            has_body_summary: !!msg.body_summary,
            has_reply_summary: !!msg.reply_summary,
            current_record_id: currentRecord.value?.id
          })
          
          // 如果当前详情对话框打开且是同一封邮件，则更新摘要显示
          if (currentRecord.value && msg.email_id === currentRecord.value.id) {
            let shouldStopPolling = false
            
            if (msg.body_summary) {
              summary.body = msg.body_summary
              summary.bodyStatus = 'ready'
              console.log('[WS] 已更新详情对话框的 body_summary')
            }
            if (msg.reply_summary) {
              summary.reply = msg.reply_summary
              summary.replyStatus = 'ready'
              console.log('[WS] 已更新详情对话框的 reply_summary')
            }
            
            // 如果两个摘要都已生成，停止轮询
            if (summary.bodyStatus !== 'generating' && summary.replyStatus !== 'generating') {
              shouldStopPolling = true
            }
            
            console.log('[WS] 收到摘要已保存推送，已更新 UI', {
              bodyStatus: summary.bodyStatus,
              replyStatus: summary.replyStatus,
              shouldStopPolling
            })
            
            // 停止轮询（如果在轮询中）
            if (shouldStopPolling && summaryCheckInterval) {
              clearInterval(summaryCheckInterval)
              summaryCheckInterval = null
              console.log('[WS] 所有摘要已生成，停止轮询')
            }
          }
          
          // 同时更新历史记录列表中的摘要（无论是否打开详情对话框）
          const record = recentEmails.value.find(r => r.id === msg.email_id)
          if (record) {
            if (msg.body_summary) {
              record.body_summary = msg.body_summary
            }
            if (msg.reply_summary) {
              record.reply_summary = msg.reply_summary
            }
            console.log('[WS] 已更新历史记录列表中的摘要:', msg.email_id)
          } else {
            console.log('[WS] 未在历史记录列表中找到邮件:', msg.email_id)
          }
        }
      } catch (e) {
        console.warn('[WS] 解析消息失败', e)
      }
    }
    ws.onclose = () => {
      console.log('[WS] 连接已关闭，5s后尝试重连')
      ws = null
      setTimeout(connectWebSocket, 5000)
    }
    ws.onerror = (e) => {
      console.error('[WS] 错误', e)
    }
  } catch (e) {
    console.error('[WS] 连接失败', e)
  }
}

// 检查摘要是否已生成（轮询）
let summaryCheckErrorCount = 0
const MAX_SUMMARY_CHECK_ERRORS = 5  // 最多允许5次连续错误

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
    const res = await historyApi.getHistory({ page: 1, page_size: 5 })
    
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
      
      // 同步更新 recentEmails 列表中的数据
      const listRecord = recentEmails.value.find(r => r.id === currentRecord.value.id)
      if (listRecord && listRecord.rawRecord) {
        if (updatedRecord.body_summary) {
          listRecord.rawRecord.body_summary = updatedRecord.body_summary
          console.log('[摘要检查] 已同步原始邮件摘要到列表')
        }
        if (updatedRecord.reply_summary) {
          listRecord.rawRecord.reply_summary = updatedRecord.reply_summary
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
      // 如果找不到记录，可能是记录已被删除或不在最近5条中
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
    
    // 如果是网络错误，记录但不立即停止（可能是后端暂时不可用）
    if (e.code === 'ERR_NETWORK' || e.message?.includes('ERR_CONNECTION_REFUSED')) {
      console.warn('[摘要检查] 网络错误，已重试', summaryCheckErrorCount, '次')
    }
    
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

// 分页变化处理
const handlePageChange = (page) => {
  pagination.currentPage = page
  fetchRecentEmails()
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1  // 切换每页条数时回到第一页
  fetchRecentEmails()
}

// 切换展开/收起
const toggleFullContent = (type) => {
  if (type === 'body') {
    showFullBody.value = !showFullBody.value
  } else {
    showFullReply.value = !showFullReply.value
  }
}

// 显示详情
const showDetail = (row) => {
  console.log('[详情对话框] 打开详情对话框，记录:', row)
  
  // 检查记录是否有效
  if (!row) {
    console.error('[详情对话框] 记录为空')
    return
  }
  
  // 确保 rawRecord 存在
  if (!row.rawRecord) {
    console.warn('[详情对话框] rawRecord 不存在，使用空对象')
    row.rawRecord = {}
  }
  
  currentRecord.value = row
  detailVisible.value = true
  
  // 重置展开状态
  showFullBody.value = false
  showFullReply.value = false
  
  // 重置摘要
  summary.body = ''
  summary.reply = ''
  summary.bodyStatus = ''
  summary.replyStatus = ''
  
  // 清除之前的轮询
  if (summaryCheckInterval) {
    clearInterval(summaryCheckInterval)
    summaryCheckInterval = null
  }
  
  // 重置错误计数
  summaryCheckErrorCount = 0
  
  // 检查是否有摘要
  const rawRecord = row.rawRecord || {}
  const hasBodySummary = rawRecord.body_summary
  const hasReplySummary = rawRecord.reply_summary
  
  // 原始邮件摘要
  if (hasBodySummary) {
    summary.body = rawRecord.body_summary
    summary.bodyStatus = 'ready'  // 已生成
    console.log('[详情对话框] 原始邮件摘要已存在，长度:', rawRecord.body_summary.length)
  } else if (rawRecord.body) {
    // 如果没有摘要，使用简单截取作为临时预览
    summary.body = rawRecord.body.length > 150 
      ? rawRecord.body.substring(0, 150) + '...' 
      : rawRecord.body
    summary.bodyStatus = 'generating'  // 生成中
    console.log('[详情对话框] 原始邮件摘要生成中，显示临时预览')
  } else {
    // 既没有摘要也没有原始内容
    summary.body = ''
    summary.bodyStatus = 'none'
    console.log('[详情对话框] 原始邮件无内容')
  }
  
  // 回复内容摘要
  // 特殊处理：无关邮件的回复内容很短，直接显示，不需要摘要
  if (rawRecord.status === 'skipped') {
    summary.reply = rawRecord.reply || ''
    summary.replyStatus = 'ready'
    console.log('[详情对话框] 无关邮件，直接显示回复内容')
  } else if (hasReplySummary) {
    summary.reply = rawRecord.reply_summary
    summary.replyStatus = 'ready'  // 已生成
    console.log('[详情对话框] 回复内容摘要已存在，长度:', rawRecord.reply_summary.length)
  } else if (rawRecord.reply) {
    // 如果没有摘要，使用简单截取作为临时预览
    summary.reply = rawRecord.reply.length > 150 
      ? rawRecord.reply.substring(0, 150) + '...' 
      : rawRecord.reply
    summary.replyStatus = 'generating'  // 生成中
    console.log('[详情对话框] 回复内容摘要生成中，显示临时预览')
  } else {
    // 既没有摘要也没有回复内容
    summary.reply = ''
    summary.replyStatus = 'none'
    console.log('[详情对话框] 回复内容无内容')
  }
  
  // 只有在摘要真正生成中时才启动轮询
  // 如果摘要已存在（status = 'ready'），不启动轮询
  const needPolling = summary.bodyStatus === 'generating' || summary.replyStatus === 'generating'
  
  if (needPolling) {
    console.log('[详情对话框] 摘要生成中，启动轮询检查', {
      bodyStatus: summary.bodyStatus,
      replyStatus: summary.replyStatus
    })
    summaryCheckInterval = setInterval(checkSummaryStatus, 2000)  // 每2秒检查一次
  } else {
    console.log('[详情对话框] 摘要已存在或无需生成，不启动轮询', {
      bodyStatus: summary.bodyStatus,
      replyStatus: summary.replyStatus
    })
  }
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  categoryChart?.resize()
  trendChart?.resize()
}

// 刷新统计数据（带防抖，避免重复请求）
let statsRefreshTimer = null
const refreshStats = () => {
  // 清除之前的定时器
  if (statsRefreshTimer) {
    clearTimeout(statsRefreshTimer)
  }
  
  // 防抖：延迟执行，避免短时间内多次刷新
  statsRefreshTimer = setTimeout(() => {
    fetchStats()
    fetchCategoryStats()
    fetchTrendStats()
    fetchRecentEmails()
    statsRefreshTimer = null
  }, 200) // 200ms 防抖延迟
}

onMounted(() => {
  // 获取所有数据
  refreshStats()
  // 初始化图表（会自动获取数据）
  initCategoryChart()
  initTrendChart()
  window.addEventListener('resize', handleResize)
  // 监听统计数据刷新事件
  window.addEventListener('stats-refresh', refreshStats)
  // 建立 WebSocket 连接以接收后端推送（用于摘要更新）
  connectWebSocket()
})

// 监听对话框关闭，清除轮询
watch(detailVisible, (visible) => {
  if (!visible && summaryCheckInterval) {
    clearInterval(summaryCheckInterval)
    summaryCheckInterval = null
    console.log('[详情对话框] 对话框已关闭，清除摘要轮询')
  }
})

// 使用 onActivated 确保从其他页面返回时也刷新统计数据
onActivated(() => {
  // 延迟刷新，避免与其他页面同时刷新导致请求冲突
  setTimeout(() => {
    refreshStats()
  }, 100)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('stats-refresh', refreshStats)
  categoryChart?.dispose()
  trendChart?.dispose()
  // 清除摘要轮询
  if (summaryCheckInterval) {
    clearInterval(summaryCheckInterval)
    summaryCheckInterval = null
  }
  // 关闭 WebSocket 连接
  if (ws) {
    try { ws.close() } catch (e) {}
    ws = null
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-cards {
    margin-bottom: 24px;
    
    .stat-card {
      transition: all 0.3s ease;
      border-radius: 12px;
      overflow: hidden;
      
      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }
      
      :deep(.el-card__body) {
        display: flex;
        align-items: center;
        padding: 24px;
        position: relative;
        overflow: hidden;
      }
      
      // 添加背景装饰
      &::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        pointer-events: none;
        transition: opacity 0.3s ease;
        opacity: 0;
      }
      
      &:hover::before {
        opacity: 1;
      }
      
      .stat-icon {
        width: 64px;
        height: 64px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        margin-right: 20px;
        flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
      }
      
      &:hover .stat-icon {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      }
      
      .stat-info {
        flex: 1;
        min-width: 0;
        
        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: var(--text-primary);
          line-height: 1.2;
          margin-bottom: 6px;
          letter-spacing: -0.5px;
          transition: color 0.3s ease;
        }
        
        .stat-label {
          font-size: 14px;
          color: var(--text-secondary);
          font-weight: 500;
          transition: color 0.3s ease;
        }
      }
      
      // 不同卡片的图标颜色
      &.stat-card-primary .stat-icon {
        background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
      }
      
      &.stat-card-success .stat-icon {
        background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
      }
      
      &.stat-card-warning .stat-icon {
        background: linear-gradient(135deg, #e6a23c 0%, #f0c78a 100%);
      }
      
      &.stat-card-danger .stat-icon {
        background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
      }
    }
  }
  
  .chart-row {
    margin-bottom: 20px;
    
    .el-col {
      margin-bottom: 20px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
  
  .chart-card {
    border-radius: 12px;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    :deep(.el-card__header) {
      border-bottom: 1px solid var(--border-color);
      padding: 16px 20px;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      color: var(--text-primary);
      
      span {
        font-size: 16px;
      }
    }
    
    .chart-container {
      height: 300px;
      padding: 10px;
    }
  }
  
  // 状态图标垂直居中
  .status-icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    
    .el-icon {
      display: inline-flex;
      align-items: center;
      vertical-align: middle;
    }
  }
  
  .recent-card {
    border-radius: 12px;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    :deep(.el-card__header) {
      border-bottom: 1px solid var(--border-color);
      padding: 16px 20px;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      color: var(--text-primary);
      
      span {
        font-size: 16px;
      }
    }
    
    :deep(.el-table) {
      border-radius: 8px;
      overflow: hidden;
    }
    
    .pagination-wrapper {
      display: flex;
      justify-content: flex-end;
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--border-color);
    }
  }
  
  .detail-content {
    .status-display {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .status-text {
        margin: 0;
        line-height: 1;
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
          font-size: 14px;
          color: var(--text-primary);
          margin: 0;
          font-weight: 600;
        }
      }
      
      .summary-box {
        padding: 16px;
        background-color: #f5f7fa;
        border-radius: 8px;
        border: 1px solid #e4e7ed;
        margin-bottom: 12px;
        
        .summary-content {
          margin-bottom: 8px;
        }
        
        .summary-text {
          font-size: 14px;
          line-height: 1.8;
          color: var(--text-primary);
        }
        
        .summary-loading {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #909399;
          font-size: 14px;
          
          .el-icon {
            font-size: 16px;
          }
        }
        
        .summary-hint {
          font-size: 12px;
          color: #909399;
          font-style: italic;
          margin-top: 8px;
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

// 响应式优化
@media (max-width: 992px) {
  .dashboard {
    .stat-cards {
      .stat-card {
        :deep(.el-card__body) {
          padding: 20px;
        }
        
        .stat-icon {
          width: 56px;
          height: 56px;
          margin-right: 16px;
        }
        
        .stat-info {
          .stat-value {
            font-size: 28px;
          }
        }
      }
    }
    
    .chart-row .el-col {
      margin-bottom: 20px;
    }
  }
}

@media (max-width: 768px) {
  .dashboard {
    .stat-cards {
      .stat-card {
        :deep(.el-card__body) {
          padding: 16px;
        }
        
        .stat-icon {
          width: 48px;
          height: 48px;
          margin-right: 12px;
        }
        
        .stat-info {
          .stat-value {
            font-size: 24px;
          }
          
          .stat-label {
            font-size: 12px;
          }
        }
      }
    }
  }
}
</style>

