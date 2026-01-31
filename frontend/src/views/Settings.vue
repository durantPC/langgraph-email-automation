<template>
  <div class="settings-page">
    <el-row :gutter="20" class="settings-row">
      <el-col :xs="24" :lg="12">
        <!-- 邮箱配置 -->
        <el-card shadow="hover" class="settings-card email-config-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Message /></el-icon>
                邮箱配置
              </span>
            </div>
          </template>
          
          <el-form :model="emailConfig" :rules="emailRules" ref="emailFormRef" label-width="100px">
            <el-form-item label="QQ邮箱" prop="email">
              <el-input v-model="emailConfig.email" placeholder="请输入QQ邮箱地址" />
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px; line-height: 1.5;">
                提示：注册时已填写邮箱，此处可修改。如果注册时未填写，请在此处配置。如需使用邮件功能，请务必配置授权码。
              </div>
            </el-form-item>
            <el-form-item label="授权码" prop="authCode">
              <el-input 
                v-model="emailConfig.authCode" 
                type="password"
                show-password
                placeholder="请输入QQ邮箱授权码" 
              />
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px; line-height: 1.5;">
                获取方法：登录QQ邮箱网页版 → 设置 → 账户 → 开启IMAP/SMTP服务 → 生成授权码
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testEmailConnection" :loading="testingEmail">
                <el-icon><Connection /></el-icon>
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 回复模板 -->
        <el-card shadow="hover" class="settings-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><EditPen /></el-icon>
                回复模板
              </span>
            </div>
          </template>
          
          <el-form :model="templateConfig" label-width="100px">
            <el-form-item label="签名">
              <el-input v-model="templateConfig.signature" placeholder="例如：Agentia 团队" />
            </el-form-item>
            <el-form-item label="问候语">
              <el-input v-model="templateConfig.greeting" placeholder="例如：尊敬的客户，您好！" />
            </el-form-item>
            <el-form-item label="结束语">
              <el-input v-model="templateConfig.closing" placeholder="例如：祝好！" />
            </el-form-item>
          </el-form>
          
          <!-- 模板预览 -->
          <el-divider content-position="left">模板预览</el-divider>
          <div class="template-preview">
            <div class="preview-content">
              <div class="preview-line">{{ templateConfig.greeting }}</div>
              <div class="preview-line preview-body">[邮件正文内容...]</div>
              <div class="preview-line">{{ templateConfig.closing }}</div>
              <div class="preview-line preview-signature">{{ templateConfig.signature }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :lg="12">
        <!-- AI配置 -->
        <el-card shadow="hover" class="settings-card ai-config-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Cpu /></el-icon>
                AI配置
              </span>
              <el-button type="primary" size="small" @click="showAddModelDialog = true">
                <el-icon><Plus /></el-icon>
                添加模型
              </el-button>
            </div>
          </template>
          
          <el-form :model="aiConfig" :rules="aiRules" ref="aiFormRef" label-width="120px">
            <el-form-item label="回复大模型" prop="replyModel">
              <el-select 
                v-model="aiConfig.replyModel" 
                style="width: 100%"
                filterable
                placeholder="选择模型"
              >
                <el-option-group label="系统默认模型">
                  <el-option 
                    v-for="model in defaultModels" 
                    :key="model.value" 
                    :label="model.label" 
                    :value="model.value"
                  >
                    <span>{{ model.label }}</span>
                    <span style="float: right; color: #8492a6; font-size: 12px;">系统API</span>
                  </el-option>
                </el-option-group>
                <el-option-group v-if="customModels.length > 0" label="自定义模型">
                  <el-option 
                    v-for="model in customModels" 
                    :key="model.id" 
                    :label="`${model.provider} - ${model.model}`" 
                    :value="model.model"
                  >
                    <span>{{ model.provider }} - {{ model.model }}</span>
                    <span style="float: right; color: #8492a6; font-size: 12px;">自定义API</span>
                  </el-option>
                </el-option-group>
              </el-select>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px; line-height: 1.5;">
                用于生成邮件回复内容的大模型（系统默认模型使用系统API，自定义模型使用您配置的API）
              </div>
            </el-form-item>
            <el-form-item label="嵌入大模型" prop="embeddingModel">
              <el-select 
                v-model="aiConfig.embeddingModel" 
                style="width: 100%"
                filterable
                placeholder="选择模型"
              >
                <el-option-group label="系统默认模型">
                  <el-option label="Qwen/Qwen3-Embedding-4B" value="Qwen/Qwen3-Embedding-4B">
                    <span>Qwen/Qwen3-Embedding-4B</span>
                    <span style="float: right; color: #8492a6; font-size: 12px;">系统API</span>
                  </el-option>
                  <el-option label="Qwen/Qwen3-Embedding-8B" value="Qwen/Qwen3-Embedding-8B">
                    <span>Qwen/Qwen3-Embedding-8B</span>
                    <span style="float: right; color: #8492a6; font-size: 12px;">系统API</span>
                  </el-option>
                  <el-option label="BAAI/bge-m3" value="BAAI/bge-m3">
                    <span>BAAI/bge-m3</span>
                    <span style="float: right; color: #8492a6; font-size: 12px;">系统API</span>
                  </el-option>
                </el-option-group>
                <el-option-group v-if="customEmbeddingModels.length > 0" label="自定义模型">
                  <el-option 
                    v-for="model in customEmbeddingModels" 
                    :key="model.id" 
                    :label="`${model.provider} - ${model.model}`" 
                    :value="model.model"
                  >
                    <span>{{ model.provider }} - {{ model.model }}</span>
                    <span style="float: right; color: #8492a6; font-size: 12px;">自定义API</span>
                  </el-option>
                </el-option-group>
              </el-select>
              <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px; line-height: 1.5;">
                用于知识库文档向量化的嵌入模型（系统默认模型使用系统API，自定义模型使用您配置的API）
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testAIConnection" :loading="testingAI">
                <el-icon><Connection /></el-icon>
                测试API
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 监控配置 -->
        <el-card shadow="hover" class="settings-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Timer /></el-icon>
                监控配置
              </span>
            </div>
          </template>
          
          <el-form :model="monitorConfig" label-width="100px">
            <el-form-item label="检查间隔">
              <el-input-number 
                v-model="monitorConfig.interval" 
                :min="1" 
                :max="60"
              />
              <span style="margin-left: 8px">分钟</span>
            </el-form-item>
            <el-form-item label="自动处理">
              <el-switch v-model="monitorConfig.autoProcess" />
              <span style="margin-left: 8px; color: #909399">监控运行时自动处理新邮件（不勾选则需人工手动点击处理）</span>
            </el-form-item>
            <el-form-item label="自动发送">
              <el-switch v-model="monitorConfig.autoSend" />
              <span style="margin-left: 8px; color: var(--text-secondary)">监控运行时自动发送回复（不勾选则需人工确认AI回复的内容）</span>
            </el-form-item>
            <el-form-item label="批量并发数量">
              <el-input-number 
                v-model="monitorConfig.batchSize" 
                :min="1" 
                :max="30"
              />
              <span style="margin-left: 8px; color: var(--text-secondary)">处理全部邮件时，每批同时处理的邮件数量（1-30，建议不超过20）</span>
              <div style="font-size: 12px; color: #f56c6c; margin-top: 4px; line-height: 1.5;">
                提示：设置过高的值可能导致内存和API调用压力增大，建议根据系统性能调整
              </div>
            </el-form-item>
            <el-form-item label="单封并发数量">
              <el-input-number 
                v-model="monitorConfig.singleEmailConcurrency" 
                :min="2" 
                :max="20"
              />
              <span style="margin-left: 8px; color: var(--text-secondary)">点击单封邮件处理按钮时，最多同时处理的邮件数量（2-20，建议不超过10）</span>
              <div style="font-size: 12px; color: #f56c6c; margin-top: 4px; line-height: 1.5;">
                提示：设置过高的值可能导致内存和API调用压力增大，建议根据系统性能调整
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
        
    <!-- 自定义模型管理 - 单独一行，撑满屏幕 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="24">
        <!-- 自定义模型管理 -->
        <el-card shadow="hover" class="settings-card">
          <template #header>
            <div class="card-header">
              <span>
                <el-icon><Cpu /></el-icon>
                自定义模型管理
              </span>
            </div>
          </template>
          
          <el-table :data="allCustomModels" style="width: 100%" empty-text="暂无自定义模型">
            <el-table-column prop="provider" label="服务商" width="150" />
            <el-table-column prop="model" label="模型名称" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === 'reply' ? 'primary' : 'success'">
                  {{ row.type === 'reply' ? '回复模型' : '嵌入模型' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="right">
              <template #default="{ row }">
                <el-button 
                  type="danger" 
                  size="small" 
                  :icon="Delete"
                  @click="deleteModel(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 保存按钮 -->
    <div class="save-actions">
      <el-button @click="resetSettings">
        <el-icon><RefreshLeft /></el-icon>
        恢复默认
      </el-button>
      <el-button type="primary" @click="saveSettings" :loading="saving">
        <el-icon><Check /></el-icon>
        保存设置
      </el-button>
    </div>
    
    <!-- 添加模型对话框 -->
    <el-dialog
      v-model="showAddModelDialog"
      title="添加模型"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="modelFormRef"
        :model="newModel"
        :rules="modelRules"
        label-width="100px"
      >
        <el-form-item label="模型类型" prop="type">
          <el-radio-group v-model="newModel.type">
            <el-radio label="reply">回复模型</el-radio>
            <el-radio label="embedding">嵌入模型</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="服务商" prop="provider">
          <el-select 
            v-model="newModel.provider" 
            placeholder="选择模型服务商"
            style="width: 100%"
            filterable
            allow-create
          >
            <el-option label="硅基流动" value="硅基流动" />
            <el-option label="OpenAI" value="OpenAI" />
            <el-option label="Anthropic" value="Anthropic" />
            <el-option label="DeepSeek" value="DeepSeek" />
            <el-option label="Moonshot" value="Moonshot" />
            <el-option label="智谱AI" value="智谱AI" />
            <el-option label="阿里云" value="阿里云" />
            <el-option label="腾讯云" value="腾讯云" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型" prop="model">
          <el-input 
            v-model="newModel.model" 
            placeholder="输入模型名称，例如：moonshotai/Kimi-K2-Thinking"
          />
        </el-form-item>
        <el-form-item label="API密钥" prop="apiKey">
          <el-input 
            v-model="newModel.apiKey" 
            type="password"
            show-password
            placeholder="输入 API 密钥"
          />
        </el-form-item>
        <el-form-item label="API地址">
          <el-input 
            v-model="newModel.apiBaseUrl" 
            placeholder="可选，留空则根据服务商自动推断"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            例如：https://api.openai.com/v1
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddModelDialog = false">取消</el-button>
        <el-button type="primary" @click="addModel" :loading="addingModel">添加模型</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { settingsApi } from '@/api'
import {
  Message, Cpu, Timer, EditPen, Connection, RefreshLeft, Check, Plus, Delete
} from '@element-plus/icons-vue'

const testingEmail = ref(false)
const testingAI = ref(false)
const saving = ref(false)
const emailFormRef = ref(null)
const aiFormRef = ref(null)

// 记录测试结果
const emailTestResult = ref(null) // null: 未测试, true: 成功, false: 失败
const aiTestResult = ref(null) // null: 未测试, true: 成功, false: 失败

const emailConfig = reactive({
  email: '',
  authCode: ''
})

// 邮箱验证规则
const validateQQEmail = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请输入QQ邮箱地址'))
    return
  }
  
  // 验证邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    callback(new Error('请输入合法的邮箱地址格式'))
    return
  }
  
  // 验证必须是QQ邮箱
  if (!value.endsWith('@qq.com')) {
    callback(new Error('请输入合法的QQ邮箱地址（必须以 @qq.com 结尾）'))
    return
  }
  
  callback()
}

const validateAuthCode = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请输入授权码'))
    return
  }
  callback()
}

const emailRules = {
  email: [
    { validator: validateQQEmail, trigger: ['blur', 'change'] }
  ],
  authCode: [
    { validator: validateAuthCode, trigger: ['blur', 'change'] }
  ]
}

const aiConfig = reactive({
  replyModel: 'moonshotai/Kimi-K2-Thinking',  // 与后端默认值保持一致
  embeddingModel: 'Qwen/Qwen3-Embedding-4B'  // 与后端默认值保持一致
})

// 系统默认模型列表
const defaultModels = [
  { label: 'moonshotai/Kimi-K2-Thinking', value: 'moonshotai/Kimi-K2-Thinking' },
  { label: 'Qwen/Qwen3-VL-32B-Thinking', value: 'Qwen/Qwen3-VL-32B-Thinking' },
  { label: 'deepseek-ai/DeepSeek-V3.1-Terminus', value: 'deepseek-ai/DeepSeek-V3.1-Terminus' },
  { label: 'zai-org/GLM-4.6', value: 'zai-org/GLM-4.6' },
  { label: 'MiniMaxAI/MiniMax-M2', value: 'MiniMaxAI/MiniMax-M2' }
]

// 自定义模型列表
const customModels = ref([])
const customEmbeddingModels = ref([])

// 计算所有自定义模型（用于表格显示）
const allCustomModels = computed(() => {
  return [
    ...customModels.value,
    ...customEmbeddingModels.value
  ]
})

// 添加模型对话框
const showAddModelDialog = ref(false)
const modelFormRef = ref(null)
const addingModel = ref(false)
const newModel = reactive({
  provider: '',
  model: '',
  apiKey: '',
  type: 'reply',  // 'reply' 或 'embedding'
  apiBaseUrl: ''  // 自定义API base URL
})

// 模型表单验证规则
const modelRules = {
  provider: [
    { required: true, message: '请选择服务商', trigger: 'change' }
  ],
  model: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  apiKey: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ]
}

// AI验证规则（移除apiKey验证）
const validateModel = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请选择模型'))
    return
  }
  callback()
}

const aiRules = {
  replyModel: [
    { validator: validateModel, trigger: ['blur', 'change'] }
  ],
  embeddingModel: [
    { validator: validateModel, trigger: ['blur', 'change'] }
  ]
}

const monitorConfig = reactive({
  interval: 15,
  autoProcess: false,
  autoSend: false,
  batchSize: 4,
  singleEmailConcurrency: 4
})

const templateConfig = reactive({
  signature: 'Agentia 团队',
  greeting: '尊敬的客户，您好！',
  closing: '祝好！'
})

// 获取设置
const fetchSettings = async () => {
  try {
    const res = await settingsApi.getSettings()
    console.log('[设置加载] 后端返回的设置:', res)
    emailConfig.email = res.email || ''
    emailConfig.authCode = res.authCode || ''  // 加载用户邮箱授权码
    // 重置测试结果（因为配置可能已更改）
    emailTestResult.value = null
    aiTestResult.value = null
    // 优先使用 replyModel，如果不存在或为空则使用 model（兼容旧配置），最后使用默认值
    if (res.replyModel && res.replyModel.trim()) {
      aiConfig.replyModel = res.replyModel.trim()
    } else if (res.model && res.model.trim()) {
      aiConfig.replyModel = res.model.trim()
    } else {
      aiConfig.replyModel = 'moonshotai/Kimi-K2-Thinking'
    }
    console.log('[设置加载] 最终使用的回复模型:', aiConfig.replyModel, 'replyModel:', res.replyModel, 'model:', res.model)
    aiConfig.embeddingModel = res.embeddingModel || 'Qwen/Qwen3-Embedding-4B'  // 与后端默认值保持一致
    monitorConfig.interval = res.interval || 15
    monitorConfig.autoProcess = res.autoProcess || false
    monitorConfig.autoSend = res.autoSend || false
    monitorConfig.batchSize = res.batchSize || 4
    monitorConfig.singleEmailConcurrency = res.singleEmailConcurrency || 4
    templateConfig.signature = res.signature || 'Agentia 团队'
    templateConfig.greeting = res.greeting || '尊敬的客户，您好！'
    templateConfig.closing = res.closing || '祝好！'
    
    // 加载自定义模型列表
    if (res.customModels && Array.isArray(res.customModels)) {
      customModels.value = res.customModels.filter(m => m.type === 'reply')
      customEmbeddingModels.value = res.customModels.filter(m => m.type === 'embedding')
    } else {
      customModels.value = []
      customEmbeddingModels.value = []
    }
  } catch (e) {
    console.error('获取设置失败', e)
  }
}

// 监听配置字段变化，重置测试结果
watch(() => emailConfig.email, () => {
  emailTestResult.value = null
})
watch(() => emailConfig.authCode, () => {
  emailTestResult.value = null
})
watch(() => aiConfig.replyModel, () => {
  aiTestResult.value = null
})
watch(() => aiConfig.embeddingModel, () => {
  aiTestResult.value = null
})

// 处理监控停止事件（当用户点击"停止"按钮时，后端会同步 autoProcess 为 false）
const handleMonitorStopped = () => {
  // 重新加载设置，以同步 autoProcess 的值
  fetchSettings()
}

// 处理监控启动事件（当用户点击"启动"按钮时，不需要同步 autoProcess）
const handleMonitorStarted = () => {
  // 启动监控不影响 autoProcess 设置，无需刷新
}

onMounted(() => {
  fetchSettings()
  
  // 同步邮箱配置和AI配置卡片的高度
  nextTick(() => {
    syncCardHeights()
  })
  
  // 监听监控停止事件，刷新设置（同步 autoProcess）
  window.addEventListener('monitor-stopped', handleMonitorStopped)
  // 监听监控启动事件（保留监听器，但不刷新设置）
  window.addEventListener('monitor-started', handleMonitorStarted)
})

onUnmounted(() => {
  // 清理事件监听器
  window.removeEventListener('monitor-stopped', handleMonitorStopped)
  window.removeEventListener('monitor-started', handleMonitorStarted)
})

// 同步两个卡片的高度
const syncCardHeights = () => {
  nextTick(() => {
    const emailCard = document.querySelector('.email-config-card')
    const aiCard = document.querySelector('.ai-config-card')
    
    if (emailCard && aiCard) {
      const emailHeight = emailCard.offsetHeight
      const aiHeight = aiCard.offsetHeight
      
      // 取两者中较大的高度，应用到较小的卡片
      if (emailHeight > aiHeight) {
        aiCard.style.minHeight = `${emailHeight}px`
      } else if (aiHeight > emailHeight) {
        emailCard.style.minHeight = `${aiHeight}px`
      }
    }
  })
}

const testEmailConnection = async () => {
  // 先进行表单验证
  if (!emailFormRef.value) {
    return
  }
  
  try {
    await emailFormRef.value.validate()
  } catch (error) {
    // 验证失败，显示第一个错误
    const firstError = Object.values(error)[0]?.[0]?.message
    if (firstError) {
      ElMessage.warning(firstError)
    }
    return
  }
  
  testingEmail.value = true
  try {
    // 传递当前输入的邮箱配置进行测试（即使未保存）
    const res = await settingsApi.testEmailConnection({
      email: emailConfig.email.trim(),
      authCode: emailConfig.authCode.trim()
    })
    if (res.success) {
      emailTestResult.value = true // 记录测试成功
      ElMessage.success(res.message || '邮箱连接成功！')
      // 测试成功后，提示用户保存配置
      ElMessageBox.confirm(
        '邮箱连接测试成功！是否立即保存配置？<br/>如果不保存，其他功能模块将无法使用此邮箱配置。',
        '保存配置',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '立即保存',
          cancelButtonText: '稍后保存',
          type: 'success'
        }
      ).then(() => {
        // 用户选择立即保存
        saveSettings()
      }).catch(() => {
        // 用户选择稍后保存，不做任何操作
      })
    } else {
      emailTestResult.value = false // 记录测试失败
      // 处理错误信息，转换为友好提示
      let errorMsg = res.message || '连接失败'
      
      // 处理常见的QQ邮箱错误
      // 注意：QQ邮箱登录失败时通常不会明确区分是邮箱错误还是授权码错误
      // 所以统一提示用户检查两者，避免误导
      if (errorMsg.includes('Login fail') || errorMsg.includes('Account is abnormal') || errorMsg.includes('登录失败')) {
        // 如果后端已经返回了详细的检查列表，直接使用
        if (errorMsg.includes('\n1.') || errorMsg.includes('请检查：')) {
          ElMessageBox.alert(
            errorMsg.replace(/\n/g, '<br/>'),
            '登录失败',
            {
              dangerouslyUseHTMLString: true,
              type: 'warning'
            }
          )
        } else {
          ElMessageBox.alert(
            '登录失败，请检查：<br/>1. 邮箱地址是否正确（确保是有效的QQ邮箱）<br/>2. 授权码是否正确<br/>3. 是否已开启IMAP/SMTP服务<br/>4. 账号是否异常或被限制',
            '登录失败',
            {
              dangerouslyUseHTMLString: true,
              type: 'warning'
            }
          )
        }
      } else if (errorMsg.includes('password is incorrect') && !errorMsg.includes('请检查：')) {
        // 只有在明确提示密码错误且不是综合提示时，才单独提示授权码错误
        ElMessage.error('授权码错误，请检查授权码是否正确，或重新生成授权码')
      } else if (errorMsg.includes('service is not open')) {
        ElMessage.error('IMAP/SMTP服务未开启，请登录QQ邮箱网页版开启该服务')
      } else if (errorMsg.includes('login frequency limited')) {
        ElMessage.error('登录频率过高，请稍后再试')
      } else if (errorMsg.includes('system is busy')) {
        ElMessage.error('系统繁忙，请稍后再试')
      } else {
        // 其他错误，统一提示检查邮箱和授权码
        ElMessageBox.alert(
          '登录失败，请检查：<br/>1. 邮箱地址是否正确（确保是有效的QQ邮箱）<br/>2. 授权码是否正确<br/>3. 是否已开启IMAP/SMTP服务',
          '连接失败',
          {
            dangerouslyUseHTMLString: true,
            type: 'warning'
          }
        )
      }
    }
  } catch (e) {
    // 处理网络错误或其他异常
    emailTestResult.value = false // 记录测试失败
    let errorMsg = e.detail || e.message || '测试失败'
    
    // 如果是400错误，可能是邮箱格式问题
    if (e.response?.status === 400) {
      errorMsg = '请检查邮箱地址和授权码是否正确'
    }
    
    ElMessage.error(errorMsg)
  } finally {
    testingEmail.value = false
  }
}

const testAIConnection = async () => {
  // 先进行表单验证
  if (!aiFormRef.value) {
    return
  }
  
  try {
    await aiFormRef.value.validate()
  } catch (error) {
    // 验证失败，显示第一个错误
    const firstError = Object.values(error)[0]?.[0]?.message
    if (firstError) {
      ElMessage.warning(firstError)
    }
    return
  }
  
  testingAI.value = true
  try {
    // 根据选择的模型确定使用的API密钥和base URL
    // 如果是自定义模型，使用自定义模型的API；否则使用系统默认API
    let apiKey = null
    let replyApiBaseUrl = null
    let embeddingApiBaseUrl = null
    
    const selectedReplyModel = customModels.value.find(m => m.model === aiConfig.replyModel)
    const selectedEmbeddingModel = customEmbeddingModels.value.find(m => m.model === aiConfig.embeddingModel)
    
    // 优先使用回复模型的API和base URL
    if (selectedReplyModel) {
      apiKey = selectedReplyModel.apiKey
      replyApiBaseUrl = selectedReplyModel.apiBaseUrl || null
    } else if (selectedEmbeddingModel) {
      // 如果回复模型不是自定义模型，使用嵌入模型的API
      apiKey = selectedEmbeddingModel.apiKey
    }
    
    // 获取嵌入模型的base URL
    if (selectedEmbeddingModel) {
      embeddingApiBaseUrl = selectedEmbeddingModel.apiBaseUrl || null
    }
    
    // 如果都不是自定义模型，apiKey为null，后端会使用系统默认API
    
    // 传递当前输入的AI配置进行测试（即使未保存）
    const res = await settingsApi.testAIConnection({
      replyModel: aiConfig.replyModel,
      embeddingModel: aiConfig.embeddingModel,
      apiKey: apiKey,  // 如果选择了自定义模型，传递其API；否则为null，使用系统默认API
      replyApiBaseUrl: replyApiBaseUrl,  // 传递回复模型的API base URL
      embeddingApiBaseUrl: embeddingApiBaseUrl  // 传递嵌入模型的API base URL
    })
    if (res.success) {
      aiTestResult.value = true // 记录测试成功
      ElMessage.success(res.message || 'API连接成功！')
      // 测试成功后，提示用户保存配置
      ElMessageBox.confirm(
        'API连接测试成功！是否立即保存配置？<br/>如果不保存，其他功能模块将无法使用此AI配置。',
        '保存配置',
        {
          dangerouslyUseHTMLString: true,
          confirmButtonText: '立即保存',
          cancelButtonText: '稍后保存',
          type: 'success'
        }
      ).then(() => {
        // 用户选择立即保存
        saveSettings()
      }).catch(() => {
        // 用户选择稍后保存，不做任何操作
      })
    } else {
      aiTestResult.value = false // 记录测试失败
      ElMessage.error(res.message || '连接失败')
    }
  } catch (e) {
    // 处理网络错误或其他异常
    aiTestResult.value = false // 记录测试失败
    let errorMsg = e.detail || e.message || '测试失败'
    
    // 如果是400错误，可能是配置问题
    if (e.response?.status === 400) {
      errorMsg = '请检查模型配置是否正确'
    }
    
    ElMessage.error(errorMsg)
  } finally {
    testingAI.value = false
  }
}

// 添加模型
const addModel = async () => {
  if (!modelFormRef.value) {
    return
  }
  
  try {
    await modelFormRef.value.validate()
  } catch (error) {
    return
  }
  
  addingModel.value = true
  try {
    const res = await settingsApi.addCustomModel({
      provider: newModel.provider,
      model: newModel.model.trim(),
      apiKey: newModel.apiKey.trim(),
      type: newModel.type,
      apiBaseUrl: newModel.apiBaseUrl.trim() || null  // 如果为空则传null
    })
    
    if (res.success) {
      ElMessage.success('模型添加成功')
      showAddModelDialog.value = false
      // 重置表单
      newModel.provider = ''
      newModel.model = ''
      newModel.apiKey = ''
      newModel.type = 'reply'
      newModel.apiBaseUrl = ''
      // 重新加载设置
      await fetchSettings()
    } else {
      ElMessage.error(res.message || '添加失败')
    }
  } catch (e) {
    ElMessage.error(e.detail || e.message || '添加失败')
  } finally {
    addingModel.value = false
  }
}

// 删除模型
const deleteModel = async (modelId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此模型吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await settingsApi.deleteCustomModel(modelId)
    if (res.success) {
      ElMessage.success('模型删除成功')
      // 如果删除的是当前使用的模型，重置为默认模型
      const deletedModel = allCustomModels.value.find(m => m.id === modelId)
      if (deletedModel) {
        if (deletedModel.type === 'reply' && aiConfig.replyModel === deletedModel.model) {
          aiConfig.replyModel = 'moonshotai/Kimi-K2-Thinking'
        }
        if (deletedModel.type === 'embedding' && aiConfig.embeddingModel === deletedModel.model) {
          aiConfig.embeddingModel = 'Qwen/Qwen3-Embedding-4B'
        }
      }
      // 重新加载设置
      await fetchSettings()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.detail || e.message || '删除失败')
    }
  }
}

const resetSettings = () => {
  ElMessage.info('已恢复默认设置')
  fetchSettings()
}

const saveSettings = async () => {
  saving.value = true
  try {
    await settingsApi.saveSettings({
      email: emailConfig.email,
      authCode: emailConfig.authCode,  // 保存用户邮箱授权码
      replyModel: aiConfig.replyModel,  // 保存回复大模型
      embeddingModel: aiConfig.embeddingModel,  // 保存嵌入大模型
      interval: monitorConfig.interval,
      autoProcess: monitorConfig.autoProcess,
      autoSend: monitorConfig.autoSend,
      batchSize: monitorConfig.batchSize,
      singleEmailConcurrency: monitorConfig.singleEmailConcurrency,
      signature: templateConfig.signature,
      greeting: templateConfig.greeting,
      closing: templateConfig.closing
    })
    ElMessage.success('设置已保存')
    // 触发自定义事件，通知 Layout.vue 刷新配置状态，并传递测试结果和监控配置
    window.dispatchEvent(new CustomEvent('settings-saved', {
      detail: {
        emailTestResult: emailTestResult.value,
        aiTestResult: aiTestResult.value,
        monitorConfig: {
          interval: monitorConfig.interval,
          autoProcess: monitorConfig.autoProcess,
          autoSend: monitorConfig.autoSend,
          batchSize: monitorConfig.batchSize,
          singleEmailConcurrency: monitorConfig.singleEmailConcurrency
        }
      }
    }))
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss" scoped>
.settings-page {
  .settings-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      
      // 确保图标和文字在同一水平线上
      span {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .el-icon {
          display: inline-flex;
          align-items: center;
          vertical-align: middle;
        }
      }
    }
  }
  
  // 调整AI配置的高度，让它和邮箱配置高度一致
  .email-config-card,
  .ai-config-card {
    // 让内容自然决定高度，不强制拉伸
    width: 100%;
  }
  
  .ai-config-card {
    :deep(.el-form-item) {
      margin-bottom: 18px; // 减少表单项间距
    }
    
    :deep(.el-form-item:last-child) {
      margin-bottom: 0; // 最后一个表单项不需要下边距
    }
  }
  
  .save-actions {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
  
  .template-preview {
    margin-top: 16px;
    padding: 16px;
    background-color: #f5f7fa;
    border-radius: 4px;
    border: 1px solid #e4e7ed;
    
    .preview-content {
      font-family: 'Courier New', monospace;
      font-size: 14px;
      line-height: 1.8;
      color: #606266;
      white-space: pre-wrap;
      
      .preview-line {
        margin-bottom: 8px;
        
        &.preview-body {
          color: #909399;
          font-style: italic;
          margin: 12px 0;
        }
        
        &.preview-signature {
          margin-top: 12px;
          font-weight: 500;
        }
      }
    }
  }
}
</style>

