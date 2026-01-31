<template>
  <div class="profile-container">
    <!-- 用户信息：现代化卡片设计 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="user-card" shadow="hover">
          <div class="user-card-header">
            <div class="user-avatar-section">
              <el-upload
                class="avatar-uploader"
                :show-file-list="false"
                :http-request="handleAvatarUpload"
                accept="image/*"
              >
                <div class="avatar-wrapper">
                  <el-avatar :size="100" class="user-avatar" :src="userInfo.avatar">
                    <el-icon :size="48"><User /></el-icon>
                  </el-avatar>
                  <div class="avatar-overlay">
                    <el-icon :size="20"><Upload /></el-icon>
                    <span>更换头像</span>
                  </div>
                </div>
              </el-upload>
            </div>
            
            <div class="user-basic-info">
              <div class="username-section">
                <h2 class="username">{{ userInfo.username }}</h2>
                <el-tag type="success" size="small" effect="plain" class="role-tag">
                  <el-icon><User /></el-icon>
                  {{ userInfo.role }}
                </el-tag>
              </div>
              
              <div class="user-details-grid">
                <div class="detail-item">
                  <div class="detail-icon">
                    <el-icon :size="18"><Message /></el-icon>
                  </div>
                  <div class="detail-content">
                    <span class="detail-label">绑定邮箱</span>
                    <div class="detail-value-wrapper">
                      <span 
                        class="detail-value" 
                        :class="{ 'value-empty': !userInfo.email }"
                      >
                        {{ userInfo.email || '未配置' }}
                      </span>
                      <el-tag 
                        v-if="userInfo.email" 
                        type="info" 
                        size="small" 
                        effect="plain"
                        class="value-tag"
                      >
                        可在系统设置中修改
                      </el-tag>
                      <el-tag 
                        v-else
                        type="warning" 
                        size="small" 
                        effect="plain"
                        class="value-tag"
                      >
                        请前往系统设置配置
                      </el-tag>
                    </div>
                  </div>
                </div>
                
                <div class="detail-item">
                  <div class="detail-icon">
                    <el-icon :size="18"><Calendar /></el-icon>
                  </div>
                  <div class="detail-content">
                    <span class="detail-label">注册时间</span>
                    <div class="detail-value-wrapper">
                      <span class="detail-value">{{ userInfo.registerTime }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="detail-item">
                  <div class="detail-icon">
                    <el-icon :size="18"><Clock /></el-icon>
                  </div>
                  <div class="detail-content">
                    <span class="detail-label">最后登录</span>
                    <div class="detail-value-wrapper">
                      <span class="detail-value">{{ userInfo.lastLogin }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <el-divider />
          
          <div class="user-actions">
            <el-button type="primary" size="default" @click="showEditDialog">
              <el-icon><Edit /></el-icon>
              编辑资料
            </el-button>
            <el-button type="danger" plain size="default" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 个人统计：独占一行 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>个人统计</span>
            </div>
          </template>
          
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-icon stat-blue">
                  <el-icon :size="24"><Message /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.totalEmails }}</div>
                  <div class="stat-label">累计处理邮件</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-icon stat-green">
                  <el-icon :size="24"><CircleCheck /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.sentReplies }}</div>
                  <div class="stat-label">发送回复数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-icon stat-orange">
                  <el-icon :size="24"><Clock /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.avgProcessTime }}</div>
                  <div class="stat-label">平均处理时间</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-icon stat-red">
                  <el-icon :size="24"><TrendCharts /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stats.thisMonthEmails }}</div>
                  <div class="stat-label">本月处理</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 账户安全：独占一行 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="security-card">
          <template #header>
            <div class="card-header">
              <el-icon><Lock /></el-icon>
              <span>账户安全</span>
            </div>
          </template>
          
          <div class="security-list">
            <div class="security-item">
              <div class="security-info">
                <el-icon :size="20"><Key /></el-icon>
                <div class="security-text">
                  <span class="title">登录密码</span>
                  <span class="desc">定期更换密码可以提高账户安全性</span>
                </div>
              </div>
              <el-button type="primary" link @click="showPasswordDialog">修改密码</el-button>
            </div>
            
            <el-divider />
            
            <div class="security-item">
              <div class="security-info">
                <el-icon :size="20"><Monitor /></el-icon>
                <div class="security-text">
                  <span class="title">登录设备</span>
                  <span class="desc">当前有 {{ activeDevicesCount }} 台设备登录</span>
                </div>
              </div>
              <el-button type="primary" link @click="showDevicesDialog">查看详情</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 个人偏好：独占一行 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="preference-card">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>个人偏好</span>
            </div>
          </template>
          
          <el-form label-width="110px" class="preference-form">
            <el-form-item label="界面主题">
              <el-radio-group v-model="preferences.theme" @change="handleThemeChange">
                <el-radio value="light">浅色模式</el-radio>
                <el-radio value="dark">深色模式</el-radio>
                <el-radio value="auto">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="消息通知">
              <el-switch v-model="preferences.notification" active-text="开启" inactive-text="关闭" />
              <span class="form-tip">新邮件到达时显示桌面通知</span>
            </el-form-item>
            
            <el-form-item label="声音提醒">
              <el-switch v-model="preferences.sound" active-text="开启" inactive-text="关闭" />
              <span class="form-tip">处理完成时播放提示音</span>
            </el-form-item>
            
            <el-form-item label="默认页面">
              <el-select v-model="preferences.defaultPage" style="width: 200px;">
                <el-option label="仪表盘" value="/dashboard" />
                <el-option label="邮件管理" value="/emails" />
                <el-option label="处理记录" value="/history" />
              </el-select>
            </el-form-item>
            
            <el-form-item class="form-actions">
              <el-button type="primary" @click="savePreferences">保存偏好设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近操作：独占一行 -->
    <el-row :gutter="20" class="section-row">
      <el-col :span="24">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span>最近操作</span>
            </div>
          </template>
          
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in recentActivities"
              :key="index"
              :timestamp="activity.time"
              :type="activity.type"
              placement="top"
            >
              <div class="activity-content">
                <el-icon :size="16"><component :is="activity.icon" /></el-icon>
                <span>{{ activity.content }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 编辑资料对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑资料" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" disabled />
          <span class="form-tip">邮箱地址在系统设置中修改</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUserInfo">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="500px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确认修改</el-button>
      </template>
    </el-dialog>
    
    <!-- 登录设备对话框 -->
    <el-dialog v-model="devicesDialogVisible" title="登录设备" width="700px">
      <el-table :data="loginDevices" style="width: 100%">
        <el-table-column prop="device" label="设备" width="150" />
        <el-table-column prop="browser" label="浏览器" width="120" />
        <el-table-column prop="ip" label="IP地址" width="130" />
        <el-table-column prop="time" label="登录时间" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.current" type="success" size="small">当前设备</el-tag>
            <el-tag v-else type="info" size="small">其他设备</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="scope">
            <el-button 
              v-if="!scope.row.current" 
              type="danger" 
              link 
              size="small"
              @click="handleLogoutDevice(scope.$index)"
            >
              下线
            </el-button>
            <el-tag v-else type="info" size="small" effect="plain">当前设备</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { statsApi, authApi, historyApi } from '@/api'
import { applyTheme } from '@/utils/theme'
import { requestNotificationPermission } from '@/utils/notification'
import {
  User, Message, Calendar, Clock, Edit, SwitchButton,
  DataAnalysis, CircleCheck, TrendCharts, Lock, Key,
  Monitor, Setting, List, Upload
} from '@element-plus/icons-vue'

const router = useRouter()

// 用户信息
const userInfo = ref({
  username: localStorage.getItem('username') || 'admin',
  email: '', // 初始化为空，从后端获取
  role: '系统管理员',
  registerTime: '2024-01-01',
  lastLogin: new Date().toLocaleString(),
  avatar: ''
})

// 统计数据
const stats = ref({
  totalEmails: 0,
  sentReplies: 0,
  avgProcessTime: '0秒',
  thisMonthEmails: 0
})

// 个人偏好
const preferences = ref({
  theme: 'light',
  notification: true,
  sound: false,
  defaultPage: '/dashboard'
})

// 最近操作
const recentActivities = ref([])

// 登录设备
const loginDevices = ref([])
// 当前活跃设备数量
const activeDevicesCount = ref(1)

// 对话框状态
const editDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const devicesDialogVisible = ref(false)

// 表单数据
const editForm = ref({
  username: '',
  email: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 获取统计数据 - 完善数据同步逻辑
const fetchStats = async () => {
  try {
    const res = await statsApi.getStats()
    console.log('获取统计数据:', res)
    
    // 同步后端数据到前端
    // 后端返回: { todayEmails, processed, pending, failed, sentReplies, thisMonthProcessed }
    stats.value.totalEmails = res.processed || 0
    stats.value.sentReplies = res.sentReplies || 0  // 使用后端返回的实际发送回复数
    stats.value.thisMonthEmails = res.thisMonthProcessed || 0  // 使用后端返回的本月处理数，不是今日邮件数
    
    // 计算平均处理时间（基于实际数据）
    if (stats.value.totalEmails > 0) {
      // 从后端获取历史记录，计算真实的平均处理时间
      try {
        const historyRes = await historyApi.getHistory({ page: 1, page_size: 100 })
        if (historyRes && historyRes.records && historyRes.records.length > 0) {
          // 计算有处理时间的记录的平均值
          let totalSeconds = 0
          let count = 0
          
          for (const record of historyRes.records) {
            const startTime = record.time
            const endTime = record.processed_time
            
            if (startTime && endTime) {
              try {
                const start = new Date(startTime.replace(/-/g, '/'))
                const end = new Date(endTime.replace(/-/g, '/'))
                const diffSeconds = Math.round((end - start) / 1000)
                
                // 只统计合理的处理时间（1秒到1小时之间）
                if (diffSeconds > 0 && diffSeconds < 3600) {
                  totalSeconds += diffSeconds
                  count++
                }
              } catch (e) {
                // 忽略时间解析错误
              }
            }
          }
          
          if (count > 0) {
            const avgSeconds = Math.round(totalSeconds / count)
            if (avgSeconds < 60) {
              stats.value.avgProcessTime = `约${avgSeconds}秒`
            } else {
              const minutes = Math.round(avgSeconds / 60)
              stats.value.avgProcessTime = `约${minutes}分钟`
            }
          } else {
            // 如果没有有效的处理时间记录，使用默认值
            stats.value.avgProcessTime = '约30秒'
          }
        } else {
          // 如果没有历史记录，使用默认值
          stats.value.avgProcessTime = '约30秒'
        }
      } catch (e) {
        console.error('计算平均处理时间失败', e)
        // 失败时使用默认值
        stats.value.avgProcessTime = '约30秒'
      }
    } else {
      stats.value.avgProcessTime = '0秒'
    }
  } catch (e) {
    console.error('获取统计数据失败', e)
    // 失败时保持当前值，不清零（避免处理邮件时统计数据被清零）
    // 只有在确实是网络错误或服务器错误时才考虑显示警告
    if (e.response?.status === 500 || !e.response) {
      // 服务器错误或网络错误，保持当前值，不显示警告（避免干扰用户）
      console.warn('获取统计数据失败，保持当前值')
    } else if (e.response?.status !== 401 && e.response?.status !== 403) {
      // 其他非认证错误，显示警告
      ElMessage.warning('获取统计数据失败，请稍后重试')
    }
    // 不清零统计数据，保持当前显示的值
  }
}

// 获取用户资料 - 从后端同步最新数据
const fetchUserProfile = async () => {
  try {
    const res = await authApi.getProfile()
    // 同步后端数据到前端（确保使用后端返回的数据，不保留旧数据）
    userInfo.value.username = res.username || localStorage.getItem('username') || 'admin'
    userInfo.value.email = res.email || '' // 如果后端返回空字符串，则清空，不使用旧值
    userInfo.value.role = res.role || userInfo.value.role
    userInfo.value.registerTime = res.registerTime || userInfo.value.registerTime
    userInfo.value.lastLogin = res.lastLogin || userInfo.value.lastLogin
    
    // 如果后端返回了头像，使用后端的头像；否则使用localStorage中的头像（按用户名隔离）
    const username = res.username || localStorage.getItem('username') || 'admin'
    if (res.avatar) {
      userInfo.value.avatar = res.avatar
      localStorage.setItem(`userAvatar-${username}`, res.avatar)
    } else {
      // 尝试从localStorage加载该用户的头像
      const savedAvatar = localStorage.getItem(`userAvatar-${username}`)
      if (savedAvatar) {
        userInfo.value.avatar = savedAvatar
      }
    }
    
    // 同步到localStorage
    localStorage.setItem('username', userInfo.value.username)
  } catch (e) {
    console.error('获取用户资料失败', e)
    // 失败时使用localStorage中的数据
    userInfo.value.username = localStorage.getItem('username') || 'admin'
  }
}

// 获取用户偏好设置 - 从后端同步
const fetchPreferences = async () => {
  try {
    const res = await authApi.getPreferences()
    // 同步后端数据到前端
    if (res.theme) preferences.value.theme = res.theme
    if (res.notification !== undefined) preferences.value.notification = res.notification
    if (res.sound !== undefined) preferences.value.sound = res.sound
    if (res.defaultPage) preferences.value.defaultPage = res.defaultPage
    
    // 应用主题
    applyTheme(preferences.value.theme)
    
    // 如果启用了通知，请求权限
    if (preferences.value.notification) {
      await requestNotificationPermission()
    }
    
    // 同时保存到localStorage作为备份（按用户名隔离）
    const username = localStorage.getItem('username') || 'admin'
    localStorage.setItem(`userPreferences-${username}`, JSON.stringify(preferences.value))
  } catch (e) {
    console.error('获取偏好设置失败', e)
    // 失败时尝试从localStorage加载（按用户名隔离）
    const username = localStorage.getItem('username') || 'admin'
    const savedPreferences = localStorage.getItem(`userPreferences-${username}`)
    if (savedPreferences) {
      try {
        preferences.value = JSON.parse(savedPreferences)
        // 应用主题
        applyTheme(preferences.value.theme)
      } catch (parseError) {
        console.error('解析偏好设置失败', parseError)
      }
    }
  }
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
    fetchActivities()
    statsRefreshTimer = null
  }, 200) // 200ms 防抖延迟
}

onMounted(() => {
  fetchUserProfile()  // 从后端获取最新用户资料
  refreshStats()
  fetchDevices()  // 加载登录设备列表
  fetchPreferences()  // 从后端获取偏好设置
  // 从浏览器缓存加载头像（优先使用缓存，避免重复上传）
  loadAvatarFromCache()
  // 监听统计数据刷新事件
  window.addEventListener('stats-refresh', refreshStats)
})

// 使用 onActivated 确保从其他页面返回时也刷新统计数据
onActivated(() => {
  // 延迟刷新，避免与其他页面同时刷新导致请求冲突
  setTimeout(() => {
    refreshStats()
    fetchActivities()
  }, 100)
})

onUnmounted(() => {
  window.removeEventListener('stats-refresh', refreshStats)
})

// 获取最近操作记录 - 从后端获取真实数据
const fetchActivities = async () => {
  try {
    const res = await authApi.getActivities(10)  // 获取最近10条操作记录
    if (res && res.activities) {
      recentActivities.value = res.activities.map(activity => ({
        time: activity.time,
        type: activity.type || 'info',
        icon: activity.icon || 'CircleCheck',
        content: activity.content
      }))
    } else {
      recentActivities.value = []
    }
  } catch (e) {
    console.error('获取最近操作记录失败', e)
    // 失败时保持空数组
    recentActivities.value = []
  }
}

// 从浏览器缓存加载头像（按用户名隔离）
const loadAvatarFromCache = () => {
  try {
    const username = localStorage.getItem('username') || 'admin'
    const savedAvatar = localStorage.getItem(`userAvatar-${username}`)
    if (savedAvatar) {
      userInfo.value.avatar = savedAvatar
      console.log('头像已从浏览器缓存加载')
    } else {
      console.log('浏览器缓存中没有头像')
    }
  } catch (error) {
    console.error('加载头像缓存失败:', error)
  }
}

// 显示编辑对话框
const showEditDialog = () => {
  editForm.value.username = userInfo.value.username
  editForm.value.email = userInfo.value.email
  editDialogVisible.value = true
}

// 保存用户信息 - 完善逻辑，连接后端API，编辑后要求重新登录
const saveUserInfo = async () => {
  // 前端验证
  if (!editForm.value.username || !editForm.value.username.trim()) {
    ElMessage.warning('请输入用户名')
    return
  }
  
  const newUsername = editForm.value.username.trim()
  if (newUsername.length < 2) {
    ElMessage.warning('用户名长度至少2位')
    return
  }
  
  if (newUsername.length > 20) {
    ElMessage.warning('用户名长度不能超过20位')
    return
  }
  
  // 如果用户名没有变化，不需要更新
  if (newUsername === userInfo.value.username) {
    editDialogVisible.value = false
    ElMessage.info('用户名未变化')
    return
  }
  
  // 显示确认对话框，警告用户更改后将重新登录
  try {
    await ElMessageBox.confirm(
      `确定要将用户名修改为 "${newUsername}" 吗？\n\n修改后需要重新登录才能生效。`,
      '确认修改',
      {
        confirmButtonText: '确定修改',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
  } catch {
    // 用户取消
    return
  }
  
  try {
    // 调用后端API更新用户资料
    const res = await authApi.updateProfile(newUsername)
    
    editDialogVisible.value = false
    
    // 如果用户名改变了，保存新用户名到 localStorage（用于提示用户）
    if (res.username && res.username !== editForm.value.username) {
      // 注意：这里先保存新用户名，但登录时用户可以使用旧用户名或新用户名登录
      // 后端会通过映射关系自动找到正确的用户名
      console.log(`用户名已更新: ${editForm.value.username} -> ${res.username}`)
    }
    
    ElMessage.success(res.message || '资料更新成功，请重新登录')
    
    // 延迟跳转到登录页
    setTimeout(() => {
      // 清除本地存储
      localStorage.removeItem('token')
      const oldUsername = localStorage.getItem('username')
      const finalNewUsername = res.username || editForm.value.username
      localStorage.removeItem('username')
      
      // 重要：迁移头像数据到新用户名（而不是删除）
      if (oldUsername && finalNewUsername && oldUsername !== finalNewUsername) {
        const oldAvatar = localStorage.getItem(`userAvatar-${oldUsername}`)
        if (oldAvatar) {
          // 将旧用户名的头像迁移到新用户名
          localStorage.setItem(`userAvatar-${finalNewUsername}`, oldAvatar)
          console.log(`头像已从 ${oldUsername} 迁移到 ${finalNewUsername}`)
        }
        // 清除旧用户名的头像（已迁移）
        localStorage.removeItem(`userAvatar-${oldUsername}`)
        // 清除所有与该用户相关的偏好设置
        localStorage.removeItem(`userPreferences-${oldUsername}`)
      }
      // 如果后端返回了新用户名，可以提示用户使用新用户名登录
      // 但为了兼容性，也允许使用旧用户名登录（后端会自动映射）
      if (res.username) {
        console.log(`提示：您可以使用新用户名 "${res.username}" 或旧用户名 "${oldUsername}" 登录`)
      }
      // 跳转到登录页
      router.push('/login')
    }, 1500)
  } catch (e) {
    console.error('更新用户资料失败', e)
    ElMessage.error(e.response?.data?.detail || '更新用户资料失败，请稍后重试')
  }
}

// 显示修改密码对话框
const showPasswordDialog = () => {
  passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  passwordDialogVisible.value = true
}

// 修改密码 - 完善逻辑，连接后端API
const changePassword = async () => {
  // 前端验证
  if (!passwordForm.value.oldPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.value.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.warning('新密码长度至少6位')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  try {
    // 调用后端API修改密码
    await authApi.changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword
    )
    
    passwordDialogVisible.value = false
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    ElMessage.success('密码修改成功，请重新登录')
    
    // 延迟跳转到登录页
    setTimeout(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      router.push('/login')
    }, 1500)
  } catch (e) {
    console.error('修改密码失败', e)
    ElMessage.error(e.response?.data?.detail || '修改密码失败，请稍后重试')
  }
}

// 获取登录设备列表 - 完善逻辑，连接后端API
const fetchDevices = async () => {
  try {
    const res = await authApi.getDevices()
    loginDevices.value = res.devices || []
    // 如果有activeCount，使用它；否则使用设备列表长度
    if (res.activeCount !== undefined) {
      activeDevicesCount.value = res.activeCount
    } else {
      activeDevicesCount.value = loginDevices.value.filter(d => d.current === true).length || 1
    }
  } catch (e) {
    console.error('获取登录设备失败', e)
    ElMessage.warning('获取登录设备失败，请稍后重试')
    // 使用默认数据
    loginDevices.value = [
      {
        device: 'Windows PC',
        browser: 'Chrome 120',
        ip: '127.0.0.1',
        time: new Date().toLocaleString(),
        current: true
      }
    ]
    activeDevicesCount.value = 1
  }
}

// 显示登录设备对话框
const showDevicesDialog = async () => {
  await fetchDevices()
  devicesDialogVisible.value = true
}

// 下线设备 - 完善逻辑，连接后端API
const handleLogoutDevice = async (deviceId) => {
  try {
    await ElMessageBox.confirm('确定要下线该设备吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await authApi.logoutDevice(deviceId)
    ElMessage.success('设备已下线')
    // 重新获取设备列表
    await fetchDevices()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('下线设备失败', e)
      ElMessage.error(e.response?.data?.detail || '下线设备失败，请稍后重试')
    }
  }
}

// 处理主题变化（实时预览）
const handleThemeChange = (theme) => {
  applyTheme(theme)
}

// 保存偏好设置 - 同步到后端
const savePreferences = async () => {
  try {
    // 调用后端API保存偏好设置
    await authApi.savePreferences({
      theme: preferences.value.theme,
      notification: preferences.value.notification,
      sound: preferences.value.sound,
      defaultPage: preferences.value.defaultPage
    })
    
    // 同时保存到localStorage作为备份（按用户名隔离）
    const username = localStorage.getItem('username') || 'admin'
    localStorage.setItem(`userPreferences-${username}`, JSON.stringify(preferences.value))
    
    // 立即应用主题变化
    applyTheme(preferences.value.theme)
    
    // 如果启用了通知，请求权限
    if (preferences.value.notification) {
      await requestNotificationPermission()
    }
    
    ElMessage.success('偏好设置已保存')
  } catch (e) {
    console.error('保存偏好设置失败', e)
    ElMessage.error(e.response?.data?.detail || '保存偏好设置失败，请稍后重试')
    
    // 失败时至少保存到localStorage并应用主题
    const username = localStorage.getItem('username') || 'admin'
    localStorage.setItem(`userPreferences-${username}`, JSON.stringify(preferences.value))
    
    // 即使保存失败，也应用主题变化
    applyTheme(preferences.value.theme)
    
    ElMessage.warning('偏好设置已保存到本地，但未同步到服务器')
  }
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    router.push('/login')
    ElMessage.success('已退出登录')
  }).catch(() => {})
}

// 上传头像（前端本地预览和缓存）
const handleAvatarUpload = (options) => {
  const file = options.file
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    options.onError && options.onError()
    return
  }
  
  // 验证文件大小（限制为2MB）
  const maxSize = 2 * 1024 * 1024 // 2MB
  if (file.size > maxSize) {
    ElMessage.error('图片大小不能超过2MB')
    options.onError && options.onError()
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const avatarData = e.target.result
    
    // 保存到localStorage（浏览器缓存，按用户名隔离）
    try {
      const username = localStorage.getItem('username') || 'admin'
      localStorage.setItem(`userAvatar-${username}`, avatarData)
      userInfo.value.avatar = avatarData
      ElMessage.success('头像已更新并缓存到浏览器')
      
      // 触发自定义事件，通知 Layout.vue 更新头像
      window.dispatchEvent(new CustomEvent('avatar-updated'))
      
      options.onSuccess && options.onSuccess()
    } catch (error) {
      // localStorage可能已满，尝试清理
      if (error.name === 'QuotaExceededError') {
        ElMessage.warning('浏览器存储空间不足，请清理后重试')
      } else {
        ElMessage.error('保存头像失败：' + error.message)
      }
      options.onError && options.onError()
    }
  }
  reader.onerror = () => {
    ElMessage.error('读取头像文件失败')
    options.onError && options.onError()
  }
  reader.readAsDataURL(file)
}
</script>

<style lang="scss" scoped>
.profile-container {
  padding: 24px;
  max-width: 1280px;
  margin: 0 auto;
  background: var(--bg-color);
  min-height: calc(100vh - 100px);
  transition: background-color 0.3s ease;
}

.section-row {
  margin-bottom: 20px;
  
  &:first-child {
    margin-top: 0;
  }
  
  .el-card {
    border-radius: 12px;
    border: none;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }
  }
}

// 用户卡片 - 现代化设计
.user-card {
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--bg-color) 0%, var(--card-bg) 100%);
  transition: background 0.3s ease;
  
  .user-card-header {
    display: flex;
    gap: 32px;
    padding: 8px 0;
    align-items: flex-start;
    
    @media (max-width: 768px) {
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
  }
  
  .user-avatar-section {
    flex-shrink: 0;
    
    .avatar-uploader {
      cursor: pointer;
    }
    
    .avatar-wrapper {
      position: relative;
      width: 100px;
      height: 100px;
      border-radius: 50%;
      overflow: hidden;
      border: 3px solid #fff;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
      
      &:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(64, 158, 255, 0.3);
      }
    }
    
    .user-avatar {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
    }
    
    .avatar-overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      color: #fff;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      opacity: 0;
      transition: opacity 0.3s;
      font-size: 12px;
      gap: 4px;
      border-radius: 50%;
    }
    
    .avatar-wrapper:hover .avatar-overlay {
      opacity: 1;
    }
  }
  
  .user-basic-info {
    flex: 1;
    min-width: 0;
    
    .username-section {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 20px;
      flex-wrap: wrap;
      
      .username {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        background: linear-gradient(135deg, var(--primary-color) 0%, #66b1ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      
      .role-tag {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
      }
    }
    
    .user-details-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      
      @media (max-width: 768px) {
        grid-template-columns: 1fr;
      }
      
      .detail-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px;
        background: var(--bg-color);
        border-radius: 8px;
        transition: all 0.3s ease;
        border: 1px solid var(--border-color-light);
        
        &:hover {
          background: var(--card-bg);
          border-color: var(--border-color);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }
        
        .detail-icon {
          width: 36px;
          height: 36px;
          border-radius: 8px;
          background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
          flex-shrink: 0;
        }
        
        .detail-content {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
          gap: 4px;
          
          .detail-label {
            font-size: 12px;
            color: var(--text-secondary);
            line-height: 1.4;
          }
          
          .detail-value-wrapper {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 2px;
            
            .detail-value {
              font-size: 15px;
              font-weight: 600;
              color: var(--primary-color);
              letter-spacing: 0.3px;
              
              &.value-empty {
                color: var(--text-secondary);
                font-weight: 400;
                font-style: italic;
              }
            }
            
            .value-tag {
              margin: 0;
              font-size: 11px;
              padding: 2px 8px;
              border-radius: 4px;
              transition: all 0.2s ease;
              
              &:hover {
                transform: scale(1.05);
              }
            }
          }
        }
      }
    }
  }
  
  .user-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    padding-top: 8px;
    
    .el-button {
      min-width: 120px;
      height: 40px;
      border-radius: 8px;
      font-weight: 500;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
    }
    
    @media (max-width: 768px) {
      flex-direction: column;
      
      .el-button {
        width: 100%;
      }
    }
  }
}

// 卡片头部 - 优化样式
.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
  transition: color 0.3s ease;
  
  .el-icon {
    color: var(--primary-color);
    font-size: 18px;
  }
}

.card-row {
  margin-bottom: 16px;
}

// 统计卡片 - 优化样式，添加hover缩放特效
.stats-card {
  margin-bottom: 16px;
  border-radius: 12px;
  
  .stat-item {
    display: flex;
    align-items: center;
    padding: 20px;
    background: var(--card-bg);
    border-radius: 10px;
    border: 1px solid var(--border-color);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    cursor: pointer;
    
    // hover缩放特效
    &:hover {
      border-color: var(--primary-color);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
      transform: scale(1.05) translateY(-4px);
    }
    
    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      margin-right: 16px;
      flex-shrink: 0;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    // 图标hover缩放特效
    &:hover .stat-icon {
      transform: scale(1.15) rotate(5deg);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    
    .stat-info {
      flex: 1;
      
      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
        transition: all 0.3s ease;
      }
      
      // 数值hover缩放特效
      &:hover .stat-value {
        transform: scale(1.1);
      }
      
      .stat-label {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 6px;
        line-height: 1.4;
        transition: color 0.3s ease;
      }
    }
    
    // hover时标签颜色变化
    &:hover .stat-label {
      color: var(--text-regular);
    }
  }

  // 图标颜色
  .stat-blue { background: linear-gradient(135deg, #409eff, #66b1ff); }
  .stat-green { background: linear-gradient(135deg, #67c23a, #85ce61); }
  .stat-orange { background: linear-gradient(135deg, #e6a23c, #f0c78a); }
  .stat-red { background: linear-gradient(135deg, #f56c6c, #fab6b6); }
}

// 安全卡片 - 优化样式，添加hover缩放特效
.security-card {
  margin-bottom: 16px;
  border-radius: 12px;
  
  .security-list {
    .security-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 20px;
      border-radius: 10px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
      
      // hover缩放特效
      &:hover {
        background: var(--bg-color);
        transform: scale(1.02);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
      }
      
      .security-info {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1;
        
        .el-icon {
          width: 44px;
          height: 44px;
          border-radius: 10px;
          background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
          color: #fff;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
        }
        
        // 图标hover缩放特效
        &:hover .el-icon {
          transform: scale(1.15) rotate(5deg);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
        }
        
        .security-text {
          .title {
            display: block;
            font-weight: 600;
            font-size: 15px;
            color: var(--text-primary);
            margin-bottom: 4px;
            transition: color 0.3s ease;
          }
          
          .desc {
            display: block;
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.4;
            transition: color 0.3s ease;
          }
        }
      }
      
      // hover时文字颜色变化
      &:hover .security-text {
        .title {
          color: var(--primary-color);
        }
        .desc {
          color: var(--text-regular);
        }
      }
      
      .el-button {
        transition: all 0.3s ease;
        
        &:hover {
          transform: scale(1.1);
        }
      }
    }
  }
}

// 偏好卡片 - 优化样式
.preference-card {
  margin-bottom: 16px;
  border-radius: 12px;
  
  .preference-form {
    max-width: 600px;
    
    .el-form-item {
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .form-actions {
      margin-top: 20px;
      text-align: right;
      
      .el-button {
        min-width: 100px;
        border-radius: 8px;
      }
    }
    
    .form-tip {
      font-size: 12px;
      color: var(--text-secondary);
      margin-left: 12px;
      line-height: 1.4;
    }
  }
}

// 活动卡片 - 优化样式
.activity-card {
  margin-bottom: 12px;
  border-radius: 12px;
  
  .el-timeline-item {
    padding-bottom: 12px;
    
    &:last-child {
      padding-bottom: 0;
    }
  }
  
  .activity-content {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: 6px;
    transition: all 0.3s ease;
    
    &:hover {
      background: var(--bg-color);
    }
    
    .el-icon {
      color: var(--primary-color);
      font-size: 16px;
    }
    
    span {
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.5;
    }
  }
}
</style>

