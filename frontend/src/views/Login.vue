<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>
    
    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo区域 -->
      <div class="login-header">
        <div class="logo">
          <el-icon :size="40" color="#409eff"><Message /></el-icon>
        </div>
        <h1 class="title">邮件自动化系统</h1>
        <p class="subtitle">AI驱动的智能客服邮件处理平台</p>
      </div>
      
      <!-- 登录表单 -->
      <el-form 
        ref="loginFormRef"
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <div class="login-options">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <el-link type="primary" :underline="false" @click="showForgotPasswordDialog">忘记密码?</el-link>
        </div>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            <el-icon v-if="!loading"><Right /></el-icon>
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 底部信息 -->
      <div class="login-footer">
        <p>
          还没有账号？
          <el-link type="primary" @click="goToRegister">立即注册</el-link>
        </p>
        <p class="copyright">© 2025 邮件自动化系统 · 基于 LangChain + LangGraph + RAG</p>
      </div>
    </div>

    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="forgotPasswordDialogVisible"
      width="500px"
      :close-on-click-modal="false"
      class="forgot-password-dialog"
      align-center
    >
      <template #header>
        <div class="forgot-password-header">
          <div class="header-icon">
            <el-icon :size="32" color="#409eff"><Lock /></el-icon>
          </div>
          <h3 class="header-title">忘记密码</h3>
          <p class="header-subtitle">通过验证邮箱来重置您的密码</p>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <div class="step-indicator">
        <div class="step-item" :class="{ active: forgotPasswordStep === 'verify', completed: forgotPasswordStep === 'reset' }">
          <div class="step-number">1</div>
          <div class="step-label">验证身份</div>
        </div>
        <div class="step-line" :class="{ completed: forgotPasswordStep === 'reset' }"></div>
        <div class="step-item" :class="{ active: forgotPasswordStep === 'reset' }">
          <div class="step-number">2</div>
          <div class="step-label">重置密码</div>
        </div>
      </div>
      
      <!-- 表单内容 -->
      <div class="forgot-password-content">
        <el-form
          ref="forgotPasswordFormRef"
          :model="forgotPasswordForm"
          :rules="forgotPasswordRules"
          label-position="top"
        >
          <!-- 第一步：验证身份 -->
          <transition name="fade-slide">
            <div v-if="forgotPasswordStep === 'verify'" class="form-step">
              <el-form-item label="用户名" prop="username">
                <el-input
                  v-model="forgotPasswordForm.username"
                  placeholder="请输入您的用户名"
                  size="large"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>
              
              <el-form-item label="注册邮箱" prop="email">
                <el-input
                  v-model="forgotPasswordForm.email"
                  placeholder="请输入注册时使用的QQ邮箱"
                  size="large"
                  :prefix-icon="Message"
                  clearable
                />
                <div class="form-tip">
                  <el-icon :size="14"><InfoFilled /></el-icon>
                  <span>请输入注册时绑定的QQ邮箱地址</span>
                </div>
              </el-form-item>
            </div>
          </transition>
          
          <!-- 第二步：重置密码 -->
          <transition name="fade-slide">
            <div v-if="forgotPasswordStep === 'reset'" class="form-step">
              <div class="success-message">
                <el-icon :size="24" color="#67c23a"><CircleCheck /></el-icon>
                <span>身份验证成功！请设置新密码</span>
              </div>
              
              <el-form-item label="新密码" prop="newPassword">
                <el-input
                  v-model="forgotPasswordForm.newPassword"
                  type="password"
                  placeholder="请输入新密码（至少6位）"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>
              
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input
                  v-model="forgotPasswordForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入新密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  clearable
                />
              </el-form-item>
            </div>
          </transition>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button 
            size="large"
            @click="forgotPasswordDialogVisible = false"
          >
            取消
          </el-button>
          <el-button
            v-if="forgotPasswordStep === 'verify'"
            type="primary"
            size="large"
            :loading="forgotPasswordLoading"
            @click="handleForgotPassword"
            class="primary-btn"
          >
            <el-icon v-if="!forgotPasswordLoading"><Right /></el-icon>
            {{ forgotPasswordLoading ? '验证中...' : '下一步' }}
          </el-button>
          <el-button
            v-else
            type="primary"
            size="large"
            :loading="forgotPasswordLoading"
            @click="handleResetPassword"
            class="primary-btn"
          >
            <el-icon v-if="!forgotPasswordLoading"><CircleCheck /></el-icon>
            {{ forgotPasswordLoading ? '重置中...' : '完成重置' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Right, Message, InfoFilled, CircleCheck } from '@element-plus/icons-vue'
import api, { authApi } from '@/api'

const router = useRouter()
const loginFormRef = ref(null)
const forgotPasswordFormRef = ref(null)
const loading = ref(false)
const forgotPasswordDialogVisible = ref(false)
const forgotPasswordLoading = ref(false)
const forgotPasswordStep = ref('verify') // 'verify' 或 'reset'

// 从localStorage加载保存的登录信息
const loadRememberedCredentials = () => {
  const remembered = localStorage.getItem('remember') === 'true'
  if (remembered) {
    const savedUsername = localStorage.getItem('rememberedUsername')
    const savedPassword = localStorage.getItem('rememberedPassword')
    if (savedUsername) {
      loginForm.username = savedUsername
    }
    if (savedPassword) {
      loginForm.password = savedPassword
    }
    loginForm.remember = true
  }
}

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

// 页面加载时恢复保存的登录信息
onMounted(() => {
  loadRememberedCredentials()
})

const forgotPasswordForm = reactive({
  username: '',
  email: '',
  newPassword: '',
  confirmPassword: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const forgotPasswordRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
    { pattern: /@qq\.com$/, message: '请输入QQ邮箱', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== forgotPasswordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 监听对话框关闭，重置表单
watch(forgotPasswordDialogVisible, (visible) => {
  if (!visible) {
    forgotPasswordStep.value = 'verify'
    forgotPasswordForm.username = ''
    forgotPasswordForm.email = ''
    forgotPasswordForm.newPassword = ''
    forgotPasswordForm.confirmPassword = ''
    if (forgotPasswordFormRef.value) {
      forgotPasswordFormRef.value.resetFields()
    }
  }
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 调用后端API进行登录验证
        const response = await api.post('/auth/login', {
          username: loginForm.username,
          password: loginForm.password
        })
        
        // 保存token和用户名
        localStorage.setItem('token', response.token)
        // 注意：response.username 是实际登录的用户名（可能是通过映射找到的新用户名）
        localStorage.setItem('username', response.username)
        console.log(`登录成功，用户名: ${response.username}`)
        
        // 处理"记住我"功能
        if (loginForm.remember) {
          // 保存"记住我"标志
          localStorage.setItem('remember', 'true')
          // 保存用户名和密码（注意：实际应用中密码应该加密存储）
          localStorage.setItem('rememberedUsername', loginForm.username)
          localStorage.setItem('rememberedPassword', loginForm.password)
        } else {
          // 如果取消"记住我"，清除保存的登录信息
          localStorage.removeItem('remember')
          localStorage.removeItem('rememberedUsername')
          localStorage.removeItem('rememberedPassword')
        }
        
        // 立即从后端获取用户偏好设置并应用主题
        let defaultPage = '/dashboard'
        try {
          const preferencesRes = await api.get('/auth/preferences')
          if (preferencesRes) {
            // 保存到localStorage
            localStorage.setItem(`userPreferences-${response.username}`, JSON.stringify(preferencesRes))
            
            // 立即应用主题
            const { applyTheme } = await import('@/utils/theme')
            if (preferencesRes.theme) {
              applyTheme(preferencesRes.theme)
            }
            
            // 获取默认页面
            if (preferencesRes.defaultPage) {
              defaultPage = preferencesRes.defaultPage
            }
          }
        } catch (prefError) {
          console.warn('获取用户偏好设置失败，使用默认设置', prefError)
          // 如果获取失败，使用默认主题
          const { initTheme } = await import('@/utils/theme')
          initTheme()
          
          // 尝试从localStorage读取默认页面
          const savedPreferences = localStorage.getItem(`userPreferences-${response.username}`)
          if (savedPreferences) {
            try {
              const preferences = JSON.parse(savedPreferences)
              if (preferences.defaultPage) {
                defaultPage = preferences.defaultPage
              }
            } catch (e) {
              console.error('解析用户偏好设置失败', e)
            }
          }
        }
        
        ElMessage.success('登录成功！')
        
        setTimeout(() => {
          router.push(defaultPage)
        }, 500)
      } catch (error) {
        // 错误处理：显示后端返回的具体错误信息
        const errorMsg = error.response?.data?.detail || error.message || '登录失败，请稍后重试'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const showForgotPasswordDialog = () => {
  forgotPasswordDialogVisible.value = true
}

const handleForgotPassword = async () => {
  if (!forgotPasswordFormRef.value) return
  
  await forgotPasswordFormRef.value.validate(async (valid) => {
    if (valid) {
      forgotPasswordLoading.value = true
      
      try {
        await authApi.forgotPassword(
          forgotPasswordForm.username,
          forgotPasswordForm.email
        )
        
        ElMessage.success('验证成功，请设置新密码')
        forgotPasswordStep.value = 'reset'
      } catch (error) {
        const errorMsg = error.response?.data?.detail || error.message || '验证失败，请稍后重试'
        ElMessage.error(errorMsg)
      } finally {
        forgotPasswordLoading.value = false
      }
    }
  })
}

const handleResetPassword = async () => {
  if (!forgotPasswordFormRef.value) return
  
  await forgotPasswordFormRef.value.validate(async (valid) => {
    if (valid) {
      forgotPasswordLoading.value = true
      
      try {
        await authApi.resetPassword(
          forgotPasswordForm.username,
          forgotPasswordForm.email,
          forgotPasswordForm.newPassword
        )
        
        ElMessage.success('密码重置成功，请使用新密码登录')
        forgotPasswordDialogVisible.value = false
        
        // 清空登录表单的密码字段
        loginForm.password = ''
      } catch (error) {
        const errorMsg = error.response?.data?.detail || error.message || '重置密码失败，请稍后重试'
        ElMessage.error(errorMsg)
      } finally {
        forgotPasswordLoading.value = false
      }
    }
  })
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

// 背景装饰
.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  
  .bg-shape {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    animation: float 6s ease-in-out infinite;
  }
  
  .shape-1 {
    width: 400px;
    height: 400px;
    top: -100px;
    left: -100px;
    animation-delay: 0s;
  }
  
  .shape-2 {
    width: 300px;
    height: 300px;
    bottom: -50px;
    right: -50px;
    animation-delay: 2s;
  }
  
  .shape-3 {
    width: 200px;
    height: 200px;
    top: 50%;
    right: 20%;
    animation-delay: 4s;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

// 登录卡片
.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
  
  .logo {
    width: 80px;
    height: 80px;
    margin: 0 auto 16px;
    background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(64, 158, 255, 0.3);
  }
  
  .title {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px;
  }
  
  .subtitle {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.login-form {
  .el-input {
    --el-input-border-radius: 8px;
  }
  
  .el-form-item {
    margin-bottom: 20px;
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
  border: none;
  
  &:hover {
    background: linear-gradient(135deg, #66b1ff 0%, #8b9cf7 100%);
  }
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  
  p {
    font-size: 14px;
    color: #606266;
    margin: 8px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    
    .el-link {
      margin-left: 0;
      vertical-align: baseline;
    }
  }
  
  .copyright {
    font-size: 11px;
    color: #909399;
    margin-top: 16px;
    display: block;
    white-space: nowrap;
    line-height: 1.5;
  }
}

// 响应式
// 忘记密码对话框样式
:deep(.forgot-password-dialog) {
  .el-dialog__header {
    padding: 0;
    border-bottom: none;
  }
  
  .el-dialog__body {
    padding: 0 24px 24px;
  }
  
  .el-dialog__footer {
    padding: 20px 24px;
    border-top: 1px solid #ebeef5;
  }
}

.forgot-password-header {
  text-align: center;
  padding: 24px 24px 20px;
  
  .header-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  }
  
  .header-title {
    font-size: 20px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px;
  }
  
  .header-subtitle {
    font-size: 14px;
    color: #909399;
    margin: 0;
  }
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 0;
  margin-bottom: 8px;
  
  .step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    
    .step-number {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #f0f2f5;
      color: #909399;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 14px;
      transition: all 0.3s ease;
      border: 2px solid transparent;
    }
    
    .step-label {
      margin-top: 8px;
      font-size: 12px;
      color: #909399;
      transition: color 0.3s ease;
    }
    
    &.active {
      .step-number {
        background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
        color: #fff;
        border-color: #409eff;
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
      }
      
      .step-label {
        color: #409eff;
        font-weight: 500;
      }
    }
    
    &.completed {
      .step-number {
        background: #67c23a;
        color: #fff;
        border-color: #67c23a;
      }
      
      .step-label {
        color: #67c23a;
      }
    }
  }
  
  .step-line {
    width: 80px;
    height: 2px;
    background: #f0f2f5;
    margin: 0 12px;
    margin-top: -18px;
    transition: background 0.3s ease;
    
    &.completed {
      background: #67c23a;
    }
  }
}

.forgot-password-content {
  min-height: 200px;
  
  .form-step {
    padding: 8px 0;
  }
  
  .el-form-item {
    margin-bottom: 20px;
    
    :deep(.el-form-item__label) {
      font-weight: 500;
      color: #606266;
      margin-bottom: 8px;
      font-size: 14px;
    }
  }
  
  .form-tip {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 6px;
    font-size: 12px;
    color: #909399;
    
    .el-icon {
      color: #409eff;
    }
  }
  
  .success-message {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: #f0f9ff;
    border: 1px solid #b3d8ff;
    border-radius: 8px;
    margin-bottom: 24px;
    color: #67c23a;
    font-size: 14px;
    font-weight: 500;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  
  .primary-btn {
    background: linear-gradient(135deg, #409eff 0%, #667eea 100%);
    border: none;
    
    &:hover {
      background: linear-gradient(135deg, #66b1ff 0%, #8b9cf7 100%);
    }
  }
}

// 过渡动画
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 480px) {
  .login-card {
    width: 90%;
    padding: 30px 20px;
  }
  
  .login-footer .copyright {
    font-size: 11px;
    white-space: normal;
    line-height: 1.5;
  }
  
  :deep(.forgot-password-dialog) {
    width: 90% !important;
    margin: 5vh auto;
  }
  
  .step-indicator {
    .step-line {
      width: 40px;
    }
  }
}
</style>

