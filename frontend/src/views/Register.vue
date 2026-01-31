<template>
  <div class="register-container">
    <!-- 背景装饰 -->
    <div class="register-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>
    
    <!-- 注册卡片 -->
    <div class="register-card">
      <!-- Logo区域 -->
      <div class="register-header">
        <div class="logo">
          <el-icon :size="40" color="#409eff"><Message /></el-icon>
        </div>
        <h1 class="title">邮件自动化系统</h1>
        <p class="subtitle">AI驱动的智能客服邮件处理平台</p>
      </div>
      
      <!-- 注册表单 -->
      <el-form 
        ref="registerFormRef"
        :model="registerForm" 
        :rules="registerRules" 
        class="register-form"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名（2-20个字符）"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password"
            placeholder="请输入密码（至少6位）"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password"
            placeholder="请确认密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="email">
          <el-input 
            v-model="registerForm.email" 
            placeholder="请输入QQ邮箱地址（可选，可在系统设置中配置）"
            size="large"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large"
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            <el-icon v-if="!loading"><Right /></el-icon>
            {{ loading ? '注册中...' : '注 册' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 底部信息 -->
      <div class="register-footer">
        <p>
          已有账号？
          <el-link type="primary" @click="goToLogin">立即登录</el-link>
        </p>
        <p class="copyright">© 2025 邮件自动化系统 · 基于 LangChain + LangGraph + RAG</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Right, Message } from '@element-plus/icons-vue'
import { authApi } from '@/api'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})

// 自定义验证规则
const validateUsername = async (rule, value, callback) => {
  // 基本格式验证
  if (!value || !value.trim()) {
    callback(new Error('请输入用户名'))
    return
  }
  
  const trimmedValue = value.trim()
  if (trimmedValue.length < 2) {
    callback(new Error('用户名长度至少2位'))
    return
  }
  
  if (trimmedValue.length > 20) {
    callback(new Error('用户名长度不能超过20位'))
    return
  }
  
  if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(trimmedValue)) {
    callback(new Error('用户名只能包含字母、数字、下划线和中文'))
    return
  }
  
  // 检查用户名是否已存在
  try {
    const res = await authApi.checkUsername(trimmedValue)
    if (!res.available) {
      callback(new Error(res.message || '用户名已存在'))
      return
    }
    callback()
  } catch (error) {
    // 如果检查接口出错，仍然允许继续（避免网络问题阻止注册）
    const errorMsg = error.response?.data?.message || error.message || '检查用户名失败'
    if (errorMsg.includes('已存在')) {
      callback(new Error(errorMsg))
    } else {
      // 网络错误等，不阻止用户继续
      callback()
    }
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  // 邮箱为可选，如果填写了则验证格式
  if (!value || !value.trim()) {
    callback() // 允许为空
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    callback(new Error('请输入正确的邮箱地址格式'))
    return
  }
  
  // 验证必须是QQ邮箱
  if (!value.endsWith('@qq.com')) {
    callback(new Error('本系统仅支持QQ邮箱，请输入QQ邮箱地址'))
    return
  }
  
  callback()
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUsername, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
    { max: 50, message: '密码长度不能超过50位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 调用后端API进行注册
        const response = await authApi.register(
          registerForm.username.trim(),
          registerForm.password,
          registerForm.email.trim()
        )
        
        ElMessage.success(response.message || '注册成功，请登录')
        
        // 延迟跳转到登录页
        setTimeout(() => {
          router.push('/login')
        }, 1500)
      } catch (error) {
        // 错误处理：显示后端返回的具体错误信息
        const errorMsg = error.response?.data?.detail || error.message || '注册失败，请稍后重试'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

// 背景装饰
.register-bg {
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

// 注册卡片
.register-card {
  width: 450px;
  padding: 40px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.register-header {
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

.register-form {
  .el-input {
    --el-input-border-radius: 8px;
  }
  
  .el-form-item {
    margin-bottom: 20px;
  }
}

.register-btn {
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

.register-footer {
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
@media (max-width: 480px) {
  .register-card {
    width: 90%;
    padding: 30px 20px;
  }
  
  .register-footer .copyright {
    font-size: 11px;
    white-space: normal;
    line-height: 1.5;
  }
}
</style>

