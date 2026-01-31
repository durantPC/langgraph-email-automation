<template>
  <div class="chat-panel">
    <!-- 快捷问题区域 -->
    <div v-if="showQuickQuestions && !hasMessages" class="quick-questions">
      <div class="quick-title">
        <span class="title-icon">💡</span>
        快速开始
      </div>
      <div class="quick-tags">
        <div
          v-for="(question, index) in quickQuestions"
          :key="index"
          class="quick-tag"
          @click="handleQuickQuestion(question)"
        >
          <span class="tag-icon">{{ tagIcons[index] }}</span>
          {{ question }}
        </div>
      </div>
    </div>
    
    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <!-- 空状态 -->
      <div v-if="!hasMessages && !loading" class="empty-state">
        <div class="empty-robot">
          <!-- 学士帽 -->
          <div class="robot-cap">
            <div class="cap-top"></div>
            <div class="cap-base"></div>
            <div class="tassel-pin"></div>
            <div class="tassel-string"></div>
            <div class="tassel-ball"></div>
          </div>
          <!-- 机器人头部 -->
          <div class="robot-body">
            <div class="robot-ear robot-ear-left"></div>
            <div class="robot-ear robot-ear-right"></div>
            <div class="robot-head">
              <div class="robot-face">
                <div class="robot-eyes">
                  <span class="eye"><span class="pupil"></span></span>
                  <span class="eye"><span class="pupil"></span></span>
                </div>
                <div class="robot-mouth"></div>
              </div>
            </div>
          </div>
        </div>
        <p class="empty-title">您好！我是MailBot 智能助手 👋</p>
        <p class="empty-desc">有什么可以帮您的？点击上方问题快速提问</p>
      </div>
      
      <!-- 消息项 -->
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="[`message-${message.role}`, { 'message-error': message.isError }]"
      >
        <!-- 头像 -->
        <div class="message-avatar">
          <div v-if="message.role === 'user'" class="avatar user-avatar">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <div v-else class="avatar assistant-avatar">
            <div class="mini-head">
              <div class="mini-face">
                <div class="mini-eyes"><span></span><span></span></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 消息内容 -->
        <div class="message-content">
          <div class="message-bubble">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <!-- 加载中 -->
      <div v-if="loading" class="message-item message-assistant">
        <div class="message-avatar">
          <div class="avatar assistant-avatar">
            <div class="mini-head">
              <div class="mini-face">
                <div class="mini-eyes"><span></span><span></span></div>
              </div>
            </div>
          </div>
        </div>
        <div class="message-content">
          <div class="message-bubble loading-bubble">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-wrapper">
        <textarea
          v-model="inputValue"
          placeholder="请输入您的问题..."
          :disabled="loading"
          @keydown.enter.exact.prevent="handleSend"
          @input="autoResize"
          rows="1"
          ref="inputRef"
        ></textarea>
        <button
          class="send-btn"
          :class="{ 'can-send': inputValue.trim() && !loading }"
          :disabled="!inputValue.trim() || loading"
          @click="handleSend"
        >
          <svg v-if="!loading" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
          <div v-else class="btn-loading">
            <span></span><span></span><span></span>
          </div>
        </button>
      </div>
      <div class="input-hint">按 Enter 发送，Shift + Enter 换行</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAiAssistantStore } from '@/stores/aiAssistant'

const props = defineProps({
  showQuickQuestions: {
    type: Boolean,
    default: true
  }
})

const store = useAiAssistantStore()
const route = useRoute()

const inputValue = ref('')
const messageListRef = ref(null)
const inputRef = ref(null)

const quickQuestions = [
  '如何接入邮箱账号？',
  '如何配置邮件处理规则？',
  '处理失败怎么排查？',
  '知识库如何使用？'
]

const tagIcons = ['📧', '⚙️', '🔧', '📚']

const messages = computed(() => store.messages)
const loading = computed(() => store.loading)
const hasMessages = computed(() => store.hasMessages)

const moduleNames = {
  '/dashboard': '仪表盘',
  '/emails': '邮件管理',
  '/history': '处理记录',
  '/knowledge': '知识库',
  '/settings': '系统设置',
  '/profile': '个人中心',
  '/ai-assistant': 'AI助教'
}

const getPageContext = () => {
  return {
    route: route.path,
    module: moduleNames[route.path] || route.meta?.title || '未知页面',
    entityId: route.params?.id || null
  }
}

const handleSend = async () => {
  if (!inputValue.value.trim() || loading.value) return
  
  const message = inputValue.value.trim()
  inputValue.value = ''
  
  // 重置输入框高度
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
  
  await store.sendMessage(message, getPageContext())
  scrollToBottom()
}

// 自动调整 textarea 高度
const autoResize = () => {
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
    inputRef.value.style.height = Math.min(inputRef.value.scrollHeight, 100) + 'px'
  }
}

const handleQuickQuestion = async (question) => {
  await store.sendMessage(question, getPageContext())
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

const formatMessage = (content) => {
  if (!content) return ''
  
  let formatted = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  
  formatted = formatted.replace(/\n/g, '<br>')
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  return formatted
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

watch(messages, () => scrollToBottom(), { deep: true })
watch(loading, () => scrollToBottom())

onMounted(() => {
  scrollToBottom()
})

defineExpose({ scrollToBottom })
</script>

<style lang="scss" scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--bg-color, #f5f7fa);
}

// 快捷问题
.quick-questions {
  padding: 18px;
  background: linear-gradient(180deg, var(--card-bg, #fff) 0%, var(--bg-color, #f5f7fa) 100%);
  
  .quick-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary, #909399);
    margin-bottom: 12px;
    
    .title-icon {
      font-size: 16px;
    }
  }
  
  .quick-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    
    .quick-tag {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 9px 14px;
      background: var(--card-bg, #fff);
      border: 1px solid var(--border-color, #dcdfe6);
      border-radius: 18px;
      font-size: 13px;
      color: var(--text-regular, #606266);
      cursor: pointer;
      transition: all 0.25s ease;
      
      .tag-icon {
        font-size: 14px;
      }
      
      &:hover {
        background: linear-gradient(135deg, #e8f4fd, #d6ecfa);
        border-color: #409eff;
        color: #409eff;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(64, 158, 255, 0.12);
      }
    }
  }
}

// 消息列表
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
  
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 40px 20px;
    
    .empty-robot {
      margin-bottom: 16px;
      width: 60px;
      height: 68px;
      position: relative;
      
      // 学士帽
      .robot-cap {
        position: absolute;
        top: -2px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10;
        width: 50px;
        
        .cap-top {
          width: 28px;
          height: 28px;
          position: relative;
          margin: 0 auto;
          
          &::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 50%, #0d0d0d 100%);
            transform: rotate(45deg) skewX(-5deg) skewY(-5deg);
            transform-origin: center;
            border-radius: 3px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.4);
          }
          
          &::after {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 10px;
            height: 10px;
            background: linear-gradient(135deg, rgba(255,255,255,0.16), transparent);
            transform: rotate(45deg) skewX(-5deg) skewY(-5deg);
            transform-origin: center;
            border-radius: 2px;
          }
        }
        
        .cap-base {
          width: 16px;
          height: 8px;
          background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
          margin: -6px auto 0;
          border-radius: 2px 2px 4px 4px;
        }
        
        .tassel-pin {
          position: absolute;
          top: 12px;
          left: 43px;
          width: 4px;
          height: 4px;
          background: radial-gradient(circle at 30% 30%, #fff3b0 0%, #ffd700 55%, #f5a623 100%);
          border-radius: 50%;
          box-shadow: 0 1px 2px rgba(245, 166, 35, 0.5);
        }
        
        .tassel-string {
          position: absolute;
          top: 16px;
          left: 44px;
          width: 2px;
          height: 12px;
          background: linear-gradient(180deg, #ffd700 0%, #f5a623 100%);
          border-radius: 1px;
        }
        
        .tassel-ball {
          position: absolute;
          top: 27px;
          left: 42px;
          width: 5px;
          height: 6px;
          background: linear-gradient(to bottom, rgba(255, 215, 0, 0.9) 0%, rgba(245, 166, 35, 0.6) 85%, transparent 100%);
          border-radius: 0 0 40% 40%;
        }
      }
      
      // 机器人身体
      .robot-body {
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 52px;
        height: 52px;
      }
      
      // 耳朵
      .robot-ear {
        position: absolute;
        width: 10px;
        height: 16px;
        background: linear-gradient(180deg, #79bbff 0%, #409eff 100%);
        border-radius: 5px;
        top: 12px;
        box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
        
        &.robot-ear-left { left: -4px; }
        &.robot-ear-right { right: -4px; }
      }
      
      // 头部
      .robot-head {
        width: 52px;
        height: 48px;
        background: linear-gradient(180deg, #a0d2ff 0%, #79bbff 30%, #409eff 100%);
        border-radius: 16px 16px 20px 20px;
        position: relative;
        box-shadow: 0 6px 16px rgba(64, 158, 255, 0.35);
      }
      
      // 面部屏幕
      .robot-face {
        position: absolute;
        top: 10px;
        left: 7px;
        right: 7px;
        height: 28px;
        background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 5px;
      }
      
      .robot-eyes {
        display: flex;
        gap: 10px;
        
        .eye {
          width: 12px;
          height: 12px;
          background: radial-gradient(circle at 40% 40%, #fff, #f0f0f0);
          border-radius: 50%;
          box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
          position: relative;
          
          .pupil {
            position: absolute;
            width: 4px;
            height: 4px;
            background: #333;
            border-radius: 50%;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
          }
        }
      }
      
      .robot-mouth {
        width: 12px;
        height: 5px;
        background: linear-gradient(180deg, #ff7b7b 0%, #e53935 100%);
        border-radius: 0 0 6px 6px;
        margin-top: 2px;
      }
    }
    
    .empty-title {
      font-size: 17px;
      font-weight: 600;
      color: var(--text-primary, #303133);
      margin: 0 0 6px 0;
    }
    
    .empty-desc {
      font-size: 13px;
      color: var(--text-secondary, #909399);
      margin: 0;
    }
  }
}

@keyframes blink {
  0%, 90%, 100% { transform: scaleY(1); }
  95% { transform: scaleY(0.1); }
}

// 消息项
.message-item {
  display: flex;
  margin-bottom: 18px;
  
  &.message-user {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-bubble {
      background: linear-gradient(135deg, #409eff, #337ecc);
      color: #fff;
      border-radius: 16px 16px 4px 16px;
      box-shadow: 0 3px 10px rgba(64, 158, 255, 0.25);
    }
    
    .message-time {
      text-align: right;
    }
  }
  
  &.message-assistant {
    .message-bubble {
      background: var(--card-bg, #fff);
      color: var(--text-primary, #303133);
      border-radius: 16px 16px 16px 4px;
      border: 1px solid var(--border-color, #e4e7ed);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
  }
  
  &.message-error {
    .message-bubble {
      background: rgba(245, 108, 108, 0.1);
      border-color: rgba(245, 108, 108, 0.3);
      color: #f56c6c;
    }
  }
}

.message-avatar {
  flex-shrink: 0;
  margin: 0 10px;
  
  .avatar {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .user-avatar {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff;
    box-shadow: 0 3px 8px rgba(102, 126, 234, 0.3);
  }
  
  .assistant-avatar {
    background: linear-gradient(180deg, #a0d2ff 0%, #79bbff 30%, #409eff 100%);
    box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
    border-radius: 10px 10px 12px 12px;
    
    .mini-head {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .mini-face {
      width: 24px;
      height: 18px;
      background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-top: 3px;
    }
    
    .mini-eyes {
      display: flex;
      justify-content: center;
      gap: 5px;
      
      span {
        width: 5px;
        height: 5px;
        background: radial-gradient(circle at 40% 40%, #fff, #f0f0f0);
        border-radius: 50%;
        box-shadow: 0 0 3px rgba(255, 255, 255, 0.5);
      }
    }
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.message-bubble {
  padding: 11px 15px;
  
  .message-text {
    font-size: 14px;
    line-height: 1.65;
    word-break: break-word;
    
    :deep(strong) {
      font-weight: 600;
      color: inherit;
    }
    
    :deep(code) {
      background: rgba(0, 0, 0, 0.06);
      padding: 2px 5px;
      border-radius: 4px;
      font-family: 'SF Mono', Consolas, monospace;
      font-size: 13px;
    }
  }
  
  &.loading-bubble {
    padding: 14px 18px;
    
    .typing-indicator {
      display: flex;
      gap: 5px;
      
      span {
        width: 7px;
        height: 7px;
        background: #409eff;
        border-radius: 50%;
        animation: typing-bounce 1.4s ease-in-out infinite;
        
        &:nth-child(1) { animation-delay: -0.32s; }
        &:nth-child(2) { animation-delay: -0.16s; }
        &:nth-child(3) { animation-delay: 0s; }
      }
    }
  }
}

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.message-time {
  font-size: 11px;
  color: var(--text-secondary, #909399);
  margin-top: 5px;
  padding: 0 4px;
}

// 输入区域
.input-area {
  padding: 14px 18px;
  background: var(--card-bg, #fff);
  border-top: 1px solid var(--border-color, #e4e7ed);
  
  .input-wrapper {
    display: flex;
    gap: 10px;
    align-items: flex-end;
    background: var(--bg-color, #f5f7fa);
    border: 1px solid var(--border-color, #dcdfe6);
    border-radius: 12px;
    padding: 10px 12px;
    transition: all 0.2s ease;
    min-height: 50px;
    
    &:focus-within {
      border-color: #409eff;
      box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
    }
    
    textarea {
      flex: 1;
      border: none;
      background: transparent;
      font-size: 14px;
      line-height: 1.6;
      color: var(--text-primary, #303133);
      resize: none;
      min-height: 28px;
      max-height: 100px;
      outline: none;
      font-family: inherit;
      padding: 4px 0;
      overflow-y: auto;
      
      &::placeholder {
        color: var(--text-secondary, #909399);
      }
      
      &:disabled {
        cursor: not-allowed;
      }
    }
    
    .send-btn {
      width: 38px;
      height: 38px;
      border: none;
      border-radius: 10px;
      background: #dcdfe6;
      color: #909399;
      cursor: not-allowed;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.25s ease;
      flex-shrink: 0;
      
      &.can-send {
        background: linear-gradient(135deg, #409eff, #337ecc);
        color: #fff;
        cursor: pointer;
        box-shadow: 0 3px 8px rgba(64, 158, 255, 0.3);
        
        &:hover {
          transform: scale(1.05);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
        }
        
        &:active {
          transform: scale(0.95);
        }
      }
      
      .btn-loading {
        display: flex;
        gap: 3px;
        
        span {
          width: 5px;
          height: 5px;
          background: #fff;
          border-radius: 50%;
          animation: typing-bounce 1.4s ease-in-out infinite;
          
          &:nth-child(1) { animation-delay: -0.32s; }
          &:nth-child(2) { animation-delay: -0.16s; }
          &:nth-child(3) { animation-delay: 0s; }
        }
      }
    }
  }
  
  .input-hint {
    font-size: 11px;
    color: var(--text-secondary, #c0c4cc);
    margin-top: 6px;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }
  
  .quick-tags .quick-tag {
    font-size: 12px;
    padding: 8px 12px;
  }
}
</style>
