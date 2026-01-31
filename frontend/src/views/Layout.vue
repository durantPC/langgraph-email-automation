<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <!-- Logo -->
      <div class="sidebar-logo" :class="{ 'collapsed': isCollapse }">
        <el-icon :size="28" color="#fff"><Message /></el-icon>
        <span v-show="!isCollapse" class="logo-text">邮件自动化</span>
      </div>
      
      <!-- 菜单 -->
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        
        <el-menu-item index="/emails">
          <el-icon><Message /></el-icon>
          <template #title>邮件管理</template>
        </el-menu-item>
        
        <el-menu-item index="/history">
          <el-icon><Document /></el-icon>
          <template #title>处理记录</template>
        </el-menu-item>
        
        <el-menu-item index="/knowledge">
          <el-icon><Collection /></el-icon>
          <template #title>知识库</template>
        </el-menu-item>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <!-- 折叠按钮 -->
          <el-icon 
            class="collapse-btn" 
            :size="20"
            @click="toggleCollapse"
          >
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
          
          <!-- 面包屑 -->
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRoute?.meta?.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <!-- 系统状态 -->
          <div class="system-status">
            <el-tag :type="systemStatus.running ? 'success' : 'info'" size="small">
              <el-icon class="status-icon"><component :is="systemStatus.running ? 'VideoPlay' : 'VideoPause'" /></el-icon>
              {{ systemStatus.running ? '监控中' : '已停止' }}
            </el-tag>
          </div>
          
          <!-- 控制按钮 -->
          <el-button-group class="control-btns">
            <el-button 
              :type="systemStatus.running ? 'danger' : 'success'" 
              size="small"
              @click="toggleSystem"
            >
              <el-icon><component :is="systemStatus.running ? 'VideoPause' : 'VideoPlay'" /></el-icon>
              {{ systemStatus.running ? '停止' : '启动' }}
            </el-button>
            <el-button type="primary" size="small" @click="refreshEmails">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-button-group>
          
          <!-- 用户下拉菜单 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" class="user-avatar" :src="userAvatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ username }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      
      <!-- 底部 -->
      <el-footer class="footer">
        <div class="footer-left">
          <el-tag :type="emailConnected ? 'success' : 'danger'" size="small" effect="plain">
            <el-icon><Connection /></el-icon>
            QQ邮箱: {{ emailConnected ? '已连接' : '未连接' }}
          </el-tag>
          <el-tag :type="apiConfigured ? 'success' : 'danger'" size="small" effect="plain">
            <el-icon><Cpu /></el-icon>
            API: {{ apiConfigured ? '正常' : '未配置' }}
          </el-tag>
        </div>
        <div class="footer-right">
          <span>v1.0.0</span>
        </div>
      </el-footer>
    </el-container>
    
    <!-- AI助教悬浮机器人 -->
    <FloatingAiBot />
    
    <!-- AI助教弹窗 -->
    <AiAssistantModal />
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { systemApi, settingsApi } from '@/api'
import {
  Message, Odometer, Document, Collection, Setting,
  Expand, Fold, User, ArrowDown, SwitchButton,
  VideoPlay, VideoPause, Refresh, Connection, Cpu
} from '@element-plus/icons-vue'
import FloatingAiBot from '@/components/ai/FloatingAiBot.vue'
import AiAssistantModal from '@/components/ai/AiAssistantModal.vue'

const router = useRouter()
const route = useRoute()

const isCollapse = ref(false)
const username = ref(localStorage.getItem('username') || 'admin')
const userAvatar = ref('') // 头像URL

const systemStatus = ref({
  running: false,
  autoProcess: false,
  lastCheck: null
})

const emailConnected = ref(false)
const apiConfigured = ref(false)

const currentRoute = computed(() => route)
const activeMenu = computed(() => route.path)

// 从浏览器缓存加载头像（按用户名隔离）
const loadAvatar = () => {
  try {
    const currentUsername = localStorage.getItem('username') || 'admin'
    const savedAvatar = localStorage.getItem(`userAvatar-${currentUsername}`)
    if (savedAvatar) {
      userAvatar.value = savedAvatar
      console.log('Layout: 头像已从浏览器缓存加载')
    } else {
      userAvatar.value = ''
      console.log('Layout: 浏览器缓存中没有头像')
    }
  } catch (error) {
    console.error('Layout: 加载头像缓存失败:', error)
    userAvatar.value = ''
  }
}

// 获取系统状态
const fetchSystemStatus = async () => {
  try {
    const res = await systemApi.getStatus()
    systemStatus.value.running = res.running
    systemStatus.value.autoProcess = res.autoProcess
    systemStatus.value.lastCheck = res.lastCheckTime
  } catch (e) {
    console.error('获取系统状态失败', e)
  }
}

// 检查配置状态
const checkConfigStatus = async (testResults = null) => {
  try {
    const res = await settingsApi.getSettings()
    
    // 检查邮箱配置：需要邮箱地址和授权码
    const hasEmailConfig = !!(res.email && res.authCode)
    
    // 如果提供了测试结果，优先使用测试结果
    if (testResults && testResults.emailTestResult !== null) {
      // 如果测试失败，即使有配置也显示未连接
      emailConnected.value = testResults.emailTestResult === true && hasEmailConfig
    } else {
      // 没有测试结果时，只检查配置是否存在
      emailConnected.value = hasEmailConfig
    }
    
    // 检查API配置：只需要回复模型和嵌入模型
    // 注意：apiKey 不再是必须的，因为系统默认模型使用后端配置的 API 密钥
    const hasAIConfig = !!(res.replyModel && res.embeddingModel)
    
    // 如果提供了测试结果，优先使用测试结果
    if (testResults && testResults.aiTestResult !== null) {
      // 如果测试失败，即使有配置也显示未配置
      apiConfigured.value = testResults.aiTestResult === true && hasAIConfig
    } else {
      // 没有测试结果时，只检查配置是否存在
      apiConfigured.value = hasAIConfig
    }
  } catch (e) {
    console.error('获取配置状态失败', e)
    emailConnected.value = false
    apiConfigured.value = false
  }
}

// 监听路由变化，从个人中心返回时刷新头像，从设置页面返回或进入时刷新配置状态
watch(() => route.path, (newPath, oldPath) => {
  loadAvatar()
  // 如果进入或离开设置页面，刷新配置状态
  if (newPath === '/settings' || oldPath === '/settings') {
    checkConfigStatus()
  }
})

// 监听自定义事件（当个人中心更新头像时）
const handleAvatarUpdated = () => {
  loadAvatar()
}

// 处理设置保存事件
const handleSettingsSaved = async (event) => {
  // 从事件中获取测试结果和监控配置
  const detail = event.detail || {}
  const testResults = {
    emailTestResult: detail.emailTestResult,
    aiTestResult: detail.aiTestResult
  }
  checkConfigStatus(testResults)
  
  // 如果监控配置发生变化，刷新系统状态
  if (detail.monitorConfig) {
    await fetchSystemStatus()
  }
}

// 处理监控停止事件（当用户点击"停止"按钮时，后端会同步 autoProcess 为 false）
const handleMonitorStopped = () => {
  // 重新加载系统状态
  fetchSystemStatus()
}

onMounted(() => {
  fetchSystemStatus()
  loadAvatar()
  checkConfigStatus()
  // 监听自定义事件
  window.addEventListener('avatar-updated', handleAvatarUpdated)
  // 监听设置保存事件，刷新配置状态（传递测试结果）
  window.addEventListener('settings-saved', handleSettingsSaved)
  // 监听监控停止事件，刷新设置（同步 autoProcess）
  window.addEventListener('monitor-stopped', handleMonitorStopped)
})

onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('avatar-updated', handleAvatarUpdated)
  window.removeEventListener('settings-saved', handleSettingsSaved)
  window.removeEventListener('monitor-stopped', handleMonitorStopped)
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const toggleSystem = async () => {
  if (systemStatus.value.running) {
    ElMessageBox.confirm('确定要停止邮件监控吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(async () => {
      try {
        await systemApi.stopMonitor()
        systemStatus.value.running = false
        systemStatus.value.autoProcess = false
        ElMessage.success('邮件监控已停止')
        // 触发自定义事件，通知设置页面刷新（因为 autoStart 已被后端同步设置为 false）
        window.dispatchEvent(new CustomEvent('monitor-stopped'))
      } catch (e) {
        ElMessage.error('停止失败')
      }
    }).catch(() => {})
  } else {
    try {
      await systemApi.startMonitor()
      systemStatus.value.running = true
      systemStatus.value.lastCheck = new Date()
      ElMessage.success('邮件监控已启动')
    } catch (e) {
      ElMessage.error('启动失败')
    }
  }
}

const refreshEmails = async () => {
  // 如果当前在邮件管理页面，不显示"正在刷新邮件..."提示，由页面内的刷新按钮统一处理
  const isEmailsPage = route.path === '/emails'
  
  if (!isEmailsPage) {
    ElMessage.info('正在刷新邮件...')
  }
  
  try {
    const res = await systemApi.refreshEmails()
    
    // 如果当前在邮件管理页面，不在这里显示成功消息，由页面内的刷新按钮统一处理
    // 如果不在邮件管理页面，显示成功消息
    if (!isEmailsPage) {
      ElMessage.success(res.message || '刷新完成')
    }
    
    // 触发自定义事件通知邮件列表刷新（如果当前在邮件管理页面）
    window.dispatchEvent(new CustomEvent('emails-refresh', { 
      detail: { 
        message: res.message,
        showMessage: isEmailsPage  // 如果在邮件管理页面，由页面内的刷新逻辑显示消息
      } 
    }))
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
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
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
      break
  }
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
}

// 侧边栏
.sidebar {
  background-color: var(--sidebar-bg);
  transition: width 0.3s, background-color 0.3s ease;
  overflow: hidden;
  
  .sidebar-logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
    background-color: var(--sidebar-bg);
    
    .logo-text {
      margin-left: 12px;
      font-size: 18px;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
    }
    
    &.collapsed {
      padding: 0;
    }
  }
  
  .el-menu {
    border-right: none;
    
    .el-menu-item {
      &:hover {
        background-color: #263445;
      }
      
      &.is-active {
        background-color: #1890ff;
        color: #fff;
      }
    }
  }
}

// 主容器
.main-container {
  display: flex;
  flex-direction: column;
}

// 顶部导航
.header {
  height: 60px;
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
  
  .header-left {
    display: flex;
    align-items: center;
    
    .collapse-btn {
      cursor: pointer;
      margin-right: 16px;
      color: var(--text-regular);
      transition: color 0.3s ease;
      
      &:hover {
        color: var(--primary-color);
      }
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .system-status {
      .status-icon {
        margin-right: 4px;
      }
    }
    
    .control-btns {
      .el-button {
        .el-icon {
          margin-right: 4px;
        }
      }
    }
    
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 4px;
      
      &:hover {
        background-color: var(--bg-color);
      }
      
      .user-avatar {
        background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
      }
      
      .username {
        margin: 0 8px;
        font-size: 14px;
        color: var(--text-regular);
      }
      
      .dropdown-icon {
        color: var(--text-secondary);
        font-size: 12px;
      }
    }
  }
}

// 主内容
.main-content {
  background-color: var(--bg-color);
  padding: 20px;
  overflow-y: auto;
  transition: background-color 0.3s ease;
}

// 底部
.footer {
  height: 40px;
  background: var(--header-bg);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  font-size: 12px;
  color: var(--text-secondary);
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
  
  .footer-left {
    display: flex;
    gap: 12px;
    
    .el-tag {
      .el-icon {
        margin-right: 4px;
      }
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

