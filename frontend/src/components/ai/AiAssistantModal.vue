<template>
  <Teleport to="body">
    <transition name="drawer">
      <div v-if="visible" class="ai-assistant-modal-mask" @click.self="handleClose">
        <div class="ai-assistant-modal">
          <!-- 头部 -->
          <div class="modal-header">
            <div class="header-left">
              <!-- 蓝色学士帽机器人头像（和AiAssistantEntry完全一样） -->
              <div class="header-avatar">
                <!-- 学士帽 -->
                <div class="avatar-cap">
                  <div class="cap-top"></div>
                  <div class="cap-base"></div>
                  <div class="tassel-pin"></div>
                  <div class="tassel-string"></div>
                  <div class="tassel-ball"></div>
                </div>
                <!-- 机器人身体 -->
                <div class="avatar-body">
                  <!-- 耳朵 -->
                  <div class="avatar-ear avatar-ear-left"></div>
                  <div class="avatar-ear avatar-ear-right"></div>
                  <!-- 头部 -->
                  <div class="avatar-head">
                    <div class="avatar-face">
                      <div class="avatar-eyes">
                        <span class="eye"><span class="pupil"></span></span>
                        <span class="eye"><span class="pupil"></span></span>
                      </div>
                      <div class="avatar-mouth"></div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="header-info">
                <span class="header-title">MailBot 智能助手</span>
                <span class="header-status">
                  <span class="status-dot"></span>
                  在线
                </span>
              </div>
            </div>
            <div class="header-actions">
              <button class="header-btn" title="新建会话" :disabled="!hasMessages" @click="handleClearConversation">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                </svg>
              </button>
              <button class="header-btn" title="在新页面打开" @click="handleOpenPage">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
                </svg>
              </button>
              <button class="header-btn close-btn" title="关闭" @click="handleClose">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 聊天面板 -->
          <div class="modal-body">
            <ChatPanel ref="chatPanelRef" :show-quick-questions="true" />
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAiAssistantStore } from '@/stores/aiAssistant'
import ChatPanel from './ChatPanel.vue'

const router = useRouter()
const store = useAiAssistantStore()
const chatPanelRef = ref(null)

const visible = computed(() => store.modalVisible)
const hasMessages = computed(() => store.hasMessages)

const handleClose = () => {
  store.closeModal()
}

const handleClearConversation = () => {
  ElMessageBox.confirm('确定要清空当前会话吗？', '新建会话', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    customClass: 'ai-assistant-confirm-dialog',
    appendTo: '.ai-assistant-modal'
  }).then(() => {
    store.clearConversation()
  }).catch(() => {})
}

const handleOpenPage = () => {
  store.closeModal()
  router.push('/ai-assistant')
}

watch(visible, (val) => {
  if (val) {
    setTimeout(() => {
      chatPanelRef.value?.scrollToBottom()
    }, 100)
  }
})
</script>

<style lang="scss" scoped>
.ai-assistant-modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.35);
  z-index: 10000;
  display: flex;
  justify-content: flex-end;
  backdrop-filter: blur(2px);
}

.ai-assistant-modal {
  width: 420px;
  max-width: 100%;
  height: 100%;
  background-color: var(--card-bg, #fff);
  box-shadow: -6px 0 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: linear-gradient(135deg, #e8f4fd 0%, #d6ecfa 100%);
  border-bottom: 1px solid rgba(64, 158, 255, 0.15);
  flex-shrink: 0;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .header-avatar {
    width: 50px;
    height: 56px;
    position: relative;
    flex-shrink: 0;
    overflow: visible;
    
    // 学士帽 - 和AiAssistantEntry完全一样
    .avatar-cap {
      position: absolute;
      top: -2px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      overflow: visible;
      width: 42px;
      
      .cap-top {
        width: 24px;
        height: 24px;
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
          box-shadow: 0 2px 4px rgba(0,0,0,0.4), inset 0 1px 1px rgba(255,255,255,0.1);
        }
        
        &::after {
          content: '';
          position: absolute;
          top: 2px;
          left: 2px;
          width: 8px;
          height: 8px;
          background: linear-gradient(135deg, rgba(255,255,255,0.16), transparent);
          transform: rotate(45deg) skewX(-5deg) skewY(-5deg);
          transform-origin: center;
          border-radius: 2px;
        }
      }
      
      .cap-base {
        width: 14px;
        height: 7px;
        background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
        margin: -5px auto 0;
        border-radius: 2px 2px 4px 4px;
      }
      
      // 流苏
      .tassel-pin {
        position: absolute;
        top: 10px;
        left: 36px;
        width: 3px;
        height: 3px;
        background: radial-gradient(circle at 30% 30%, #fff3b0 0%, #ffd700 55%, #f5a623 100%);
        border-radius: 50%;
        box-shadow: 0 1px 2px rgba(245, 166, 35, 0.5);
        z-index: 12;
      }
      
      .tassel-string {
        position: absolute;
        top: 13px;
        left: 37px;
        width: 2px;
        height: 10px;
        background: linear-gradient(180deg, #ffd700 0%, #f5a623 100%);
        border-radius: 1px;
        z-index: 11;
      }
      
      .tassel-ball {
        position: absolute;
        top: 22px;
        left: 35px;
        width: 4px;
        height: 5px;
        background: linear-gradient(to bottom, rgba(255, 215, 0, 0.9) 0%, rgba(245, 166, 35, 0.6) 85%, transparent 100%);
        border-radius: 0 0 40% 40%;
        z-index: 11;
      }
    }
    
    // 机器人身体
    .avatar-body {
      position: absolute;
      bottom: 0;
      left: 50%;
      transform: translateX(-50%);
      width: 44px;
      height: 44px;
    }
    
    // 耳朵
    .avatar-ear {
      position: absolute;
      width: 8px;
      height: 14px;
      background: linear-gradient(180deg, #79bbff 0%, #409eff 100%);
      border-radius: 4px;
      top: 10px;
      box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
      
      &::after {
        content: '';
        position: absolute;
        top: 2px;
        width: 3px;
        height: 7px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 2px;
      }
      
      &.avatar-ear-left {
        left: -3px;
        &::after { left: 2px; }
      }
      &.avatar-ear-right {
        right: -3px;
        &::after { right: 2px; }
      }
    }
    
    // 头部
    .avatar-head {
      width: 44px;
      height: 40px;
      background: linear-gradient(180deg, #a0d2ff 0%, #79bbff 30%, #409eff 100%);
      border-radius: 14px 14px 16px 16px;
      position: relative;
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.35), inset 0 2px 6px rgba(255, 255, 255, 0.4);
    }
    
    // 面部屏幕
    .avatar-face {
      position: absolute;
      top: 8px;
      left: 6px;
      right: 6px;
      height: 24px;
      background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding-top: 4px;
    }
    
    .avatar-eyes {
      display: flex;
      gap: 8px;
      
      .eye {
        width: 10px;
        height: 10px;
        background: radial-gradient(circle at 40% 40%, #fff, #f0f0f0);
        border-radius: 50%;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.6);
        position: relative;
        
        .pupil {
          position: absolute;
          width: 3px;
          height: 3px;
          background: #333;
          border-radius: 50%;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
        }
      }
    }
    
    .avatar-mouth {
      width: 10px;
      height: 4px;
      background: linear-gradient(180deg, #ff7b7b 0%, #e53935 100%);
      border-radius: 0 0 5px 5px;
      margin-top: 2px;
    }
  }
  
  .header-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    
    .header-title {
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }
    
    .header-status {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 12px;
      color: #67c23a;
      
      .status-dot {
        width: 6px;
        height: 6px;
        background: #67c23a;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
      }
    }
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .header-btn {
      width: 34px;
      height: 34px;
      border: none;
      background: transparent;
      border-radius: 8px;
      color: #606266;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      
      &:hover:not(:disabled) {
        background: rgba(64, 158, 255, 0.1);
        color: #409eff;
      }
      
      &:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
      
      &.close-btn:hover {
        background: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }
    }
  }
}

.modal-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

// 抽屉动画
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  .ai-assistant-modal {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
}

.drawer-enter-from,
.drawer-leave-to {
  background-color: rgba(0, 0, 0, 0);
  backdrop-filter: blur(0px);
  
  .ai-assistant-modal {
    transform: translateX(100%);
  }
}

@media (max-width: 480px) {
  .ai-assistant-modal {
    width: 100%;
  }
}

:global(.theme-dark) {
  .modal-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a3352 100%);
    border-bottom-color: rgba(64, 158, 255, 0.1);
    
    .header-info {
      .header-title {
        color: #f0f0f0;
      }
    }
    
    .header-actions .header-btn {
      color: #a0a0a0;
      
      &:hover:not(:disabled) {
        background: rgba(64, 158, 255, 0.15);
        color: #66b1ff;
      }
      
      &.close-btn:hover {
        background: rgba(245, 108, 108, 0.15);
        color: #ff6b6b;
      }
    }
  }
}

// 自定义确认对话框样式 - 让它显示在右侧面板内
:global(.ai-assistant-confirm-dialog) {
  max-width: 280px !important;
  
  .el-message-box__header {
    padding: 12px 16px 8px;
  }
  
  .el-message-box__title {
    font-size: 15px;
  }
  
  .el-message-box__content {
    padding: 8px 16px 12px;
    font-size: 14px;
  }
  
  .el-message-box__btns {
    padding: 8px 16px 12px;
  }
}
</style>
