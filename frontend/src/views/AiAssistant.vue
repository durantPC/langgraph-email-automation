<template>
  <div class="ai-assistant-page">
    <!-- 页面头部 -->
    <el-card shadow="hover" class="page-header-card">
      <div class="page-header">
        <div class="header-left">
          <div class="header-icon">
            <el-icon :size="28"><Service /></el-icon>
          </div>
          <div class="header-info">
            <h2 class="page-title">AI 助教</h2>
            <p class="page-desc">智能问答助手，帮助您解答系统使用问题</p>
          </div>
        </div>
        
        <div class="header-actions">
          <!-- 显示/隐藏悬浮机器人开关 -->
          <div class="bot-switch">
            <span class="switch-label">显示悬浮机器人</span>
            <el-switch
              v-model="showBot"
              @change="handleBotVisibilityChange"
            />
          </div>
          
          <!-- 新建会话按钮 -->
          <el-button
            type="primary"
            plain
            :disabled="!hasMessages"
            @click="handleClearConversation"
          >
            <el-icon><RefreshRight /></el-icon>
            新建会话
          </el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 聊天区域 -->
    <el-card shadow="hover" class="chat-card">
      <ChatPanel ref="chatPanelRef" :show-quick-questions="true" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useAiAssistantStore } from '@/stores/aiAssistant'
import ChatPanel from '@/components/ai/ChatPanel.vue'
import { Service, RefreshRight } from '@element-plus/icons-vue'

const store = useAiAssistantStore()
const chatPanelRef = ref(null)

// 计算属性
const hasMessages = computed(() => store.hasMessages)
const showBot = computed({
  get: () => !store.botHidden,
  set: (val) => {
    if (val) {
      store.showBot()
    } else {
      store.hideBot()
    }
  }
})

/**
 * 处理机器人显示状态变化
 */
const handleBotVisibilityChange = (visible) => {
  if (visible) {
    store.showBot()
  } else {
    store.hideBot()
  }
}

/**
 * 清空会话
 */
const handleClearConversation = () => {
  ElMessageBox.confirm('确定要清空当前会话吗？', '新建会话', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    store.clearConversation()
  }).catch(() => {})
}

// 组件挂载时滚动到底部
onMounted(() => {
  chatPanelRef.value?.scrollToBottom()
})
</script>

<style lang="scss" scoped>
.ai-assistant-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header-card {
  flex-shrink: 0;
  border-radius: 12px;
  
  :deep(.el-card__body) {
    padding: 20px 24px;
  }
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .header-icon {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
    flex-shrink: 0;
  }
  
  .header-info {
    .page-title {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 6px 0;
    }
    
    .page-desc {
      font-size: 14px;
      color: var(--text-secondary);
      margin: 0;
    }
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .bot-switch {
      display: flex;
      align-items: center;
      gap: 10px;
      
      .switch-label {
        font-size: 14px;
        color: var(--text-regular);
      }
    }
    
    .el-button {
      border-radius: 8px;
      
      .el-icon {
        margin-right: 6px;
      }
    }
  }
}

.chat-card {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0; // 重要：允许flex子元素收缩
  
  :deep(.el-card__body) {
    padding: 0;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
}

// 响应式
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    
    .header-actions {
      width: 100%;
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
      
      .bot-switch {
        width: 100%;
        justify-content: space-between;
      }
      
      .el-button {
        width: 100%;
      }
    }
  }
}
</style>

