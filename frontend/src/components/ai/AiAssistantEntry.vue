<template>
  <el-card shadow="hover" class="ai-assistant-entry">
    <div class="entry-content">
      <!-- 左侧：机器人和信息 -->
      <div class="entry-left">
        <!-- 可爱的蓝色机器人（参考右下角浮动机器人风格） -->
        <div class="cute-robot">
          <!-- 学士帽 -->
          <div class="graduation-cap">
            <div class="cap-top"></div>
            <div class="cap-base"></div>
            <!-- 流苏放在cap-top外面，避免被rotate(45deg)影响 -->
            <div class="tassel-pin"></div>
            <div class="tassel-string"></div>
            <div class="tassel-ball"></div>
          </div>
          
          <!-- 机器人身体 -->
          <div class="robot-body">
            <!-- 左耳 -->
            <div class="ear ear-left"></div>
            <!-- 右耳 -->
            <div class="ear ear-right"></div>
            
            <!-- 头部主体 -->
            <div class="head">
              <!-- 面部屏幕 -->
              <div class="face-screen">
                <!-- 眼睛 -->
                <div class="eyes">
                  <div class="eye eye-left">
                    <div class="pupil"></div>
                  </div>
                  <div class="eye eye-right">
                    <div class="pupil"></div>
                  </div>
                </div>
                <!-- 嘴巴 -->
                <div class="mouth"></div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="entry-info">
          <h3 class="entry-title">
            <span>MailBot 智能助手</span>
            <el-tag size="small" type="primary" effect="plain" class="smart-tag">智能</el-tag>
          </h3>
          <p class="entry-desc">随时解答系统使用、配置方法、故障排查等问题</p>
        </div>
      </div>
      
      <!-- 右侧：操作按钮 -->
      <div class="entry-actions">
        <el-button type="primary" class="action-btn primary-btn" @click="handleOpenModal">
          <el-icon><ChatDotRound /></el-icon>
          <span>打开浮窗</span>
        </el-button>
        <el-button class="action-btn secondary-btn" @click="handleGoToPage">
          <el-icon><FullScreen /></el-icon>
          <span>进入助手</span>
        </el-button>
        <el-button class="action-btn history-btn" @click="handleOpenHistory">
          <el-icon><Clock /></el-icon>
          <span>聊天记录</span>
        </el-button>
      </div>
    </div>
    
    <!-- 聊天记录抽屉 -->
    <el-drawer
      v-model="showHistoryDrawer"
      title="聊天记录"
      direction="rtl"
      size="420px"
      :append-to-body="true"
    >
      <div class="history-container">
        <!-- 加载中 -->
        <div v-if="historyLoading" class="history-loading">
          <el-icon class="is-loading" :size="32" color="#409eff"><Loading /></el-icon>
          <p>加载中...</p>
        </div>
        
        <!-- 会话列表 -->
        <template v-else-if="!selectedConversation">
          <div v-if="conversationsList.length === 0" class="history-empty">
            <el-icon :size="48" color="#c0c4cc"><ChatDotRound /></el-icon>
            <p>暂无聊天记录</p>
            <p class="history-tip">新建会话后，记录会自动保存到这里</p>
          </div>
          <div v-else class="history-list">
            <div
              v-for="conv in conversationsList"
              :key="conv.id"
              class="conversation-item"
              @click="handleViewConversation(conv.id)"
            >
              <div class="conv-header">
                <span class="conv-title">{{ conv.title }}</span>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click.stop="handleDeleteConversation(conv.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <div class="conv-meta">
                <span class="conv-count">{{ conv.messageCount }} 条消息</span>
                <span class="conv-time">{{ formatDate(conv.createdAt) }}</span>
              </div>
            </div>
          </div>
          <div v-if="conversationsList.length > 0" class="history-footer">
            <el-button type="danger" plain size="small" @click="handleClearAllHistory">
              <el-icon><Delete /></el-icon>
              清空所有记录
            </el-button>
          </div>
        </template>
        
        <!-- 会话详情 -->
        <template v-else>
          <div class="detail-header">
            <el-button link @click="selectedConversation = null">
              <el-icon><ArrowLeft /></el-icon>
              返回列表
            </el-button>
            <span class="detail-title">{{ selectedConversation.title }}</span>
          </div>
          <div class="history-messages">
            <div
              v-for="msg in selectedConversation.messages"
              :key="msg.id"
              class="history-item"
              :class="[`history-${msg.role}`, { 'history-error': msg.isError }]"
            >
              <div class="history-role">
                <span v-if="msg.role === 'user'" class="role-tag user-tag">我</span>
                <span v-else class="role-tag assistant-tag">AI</span>
                <span class="history-time">{{ formatTime(msg.timestamp) }}</span>
              </div>
              <div class="history-content">{{ msg.content }}</div>
            </div>
          </div>
        </template>
      </div>
    </el-drawer>
    
    <!-- 快捷问题 -->
    <div class="quick-questions">
      <div class="quick-header">
        <el-icon><QuestionFilled /></el-icon>
        <span>快捷问题</span>
      </div>
      <div class="quick-tags">
        <div
          v-for="(question, index) in quickQuestions"
          :key="index"
          class="quick-tag"
          @click="handleQuickQuestion(question)"
        >
          <el-icon><Right /></el-icon>
          {{ question }}
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAiAssistantStore } from '@/stores/aiAssistant'
import { ChatDotRound, FullScreen, QuestionFilled, Right, Clock, Delete, Loading, ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()
const store = useAiAssistantStore()

const showHistoryDrawer = ref(false)
const historyLoading = ref(false)
const conversationsList = ref([])
const selectedConversation = ref(null)

const quickQuestions = [
  '如何接入邮箱账号？',
  '如何配置邮件处理规则？',
  '处理失败怎么排查？',
  '知识库如何使用？'
]

const handleOpenModal = () => {
  store.openModal()
}

const handleGoToPage = () => {
  router.push('/ai-assistant')
}

const handleQuickQuestion = (question) => {
  store.openModalWithMessage(question, {
    route: '/dashboard',
    module: '仪表盘',
    entityId: null
  })
}

// 打开聊天记录抽屉
const handleOpenHistory = async () => {
  showHistoryDrawer.value = true
  selectedConversation.value = null
  historyLoading.value = true
  
  try {
    conversationsList.value = await store.getConversationsList()
  } catch (e) {
    console.error('获取聊天记录失败:', e)
  } finally {
    historyLoading.value = false
  }
}

// 查看会话详情
const handleViewConversation = async (convId) => {
  historyLoading.value = true
  try {
    const detail = await store.getConversationDetail(convId)
    if (detail) {
      selectedConversation.value = detail
    }
  } catch (e) {
    ElMessage.error('获取会话详情失败')
  } finally {
    historyLoading.value = false
  }
}

// 删除单个会话
const handleDeleteConversation = async (convId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条聊天记录吗？', '删除记录', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const success = await store.deleteConversation(convId)
    if (success) {
      conversationsList.value = conversationsList.value.filter(c => c.id !== convId)
      ElMessage.success('删除成功')
    }
  } catch (e) {
    // 用户取消
  }
}

// 清空所有记录
const handleClearAllHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有聊天记录吗？此操作不可恢复！', '清空所有记录', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const success = await store.clearAllConversations()
    if (success) {
      conversationsList.value = []
      ElMessage.success('已清空所有记录')
    }
  } catch (e) {
    // 用户取消
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}
</script>

<style lang="scss" scoped>
.ai-assistant-entry {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #e8f4fd 0%, #d6ecfa 50%, #c4e3f7 100%);
  border: 1px solid rgba(64, 158, 255, 0.2);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(64, 158, 255, 0.15);
    border-color: rgba(64, 158, 255, 0.3);
    
    .cute-robot .eyes .eye .pupil {
      animation: look-around 2s ease-in-out;
    }
  }
  
  :deep(.el-card__body) {
    padding: 20px 24px;
  }
}

.entry-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.entry-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

// ========== 可爱机器人样式 ==========
.cute-robot {
  width: 60px;
  height: 68px;
  position: relative;
  flex-shrink: 0;
  overflow: visible;
}

// 学士帽 - 扁平方形样式
.graduation-cap {
  position: absolute;
  top: -2px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  overflow: visible;
  width: 50px;  // 确保有足够空间显示流苏
  
  // 方形帽顶（菱形视角）
  .cap-top {
    width: 28px;
    height: 28px;
    position: relative;
    margin: 0 auto;  // 居中
    
    // 帽顶主体（只给伪元素做旋转，避免影响内部流苏定位）
    &::before {
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 50%, #0d0d0d 100%);
      transform: rotate(45deg) skewX(-5deg) skewY(-5deg);
      transform-origin: center;
      border-radius: 3px;
      box-shadow: 
        0 2px 4px rgba(0,0,0,0.4),
        inset 0 1px 1px rgba(255,255,255,0.1);
    }

    // 帽顶高光
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
      opacity: 0.95;
      pointer-events: none;
    }
  }  // 关闭 .cap-top

  // 流苏挂点（扣子）- 放在菱形右顶点（相对于graduation-cap）
  // graduation-cap 宽50px，cap-top 28px 居中(左边距11px)
  // 菱形右顶点相对于cap-top是(33.8, 14)，相对于graduation-cap是(44.8, 14)
  .tassel-pin {
    position: absolute;
    top: 12px;   // 14 - 2（扣子半径）
    left: 43px;  // 44.8 - 2（扣子半径）
    width: 4px;
    height: 4px;
    background: radial-gradient(circle at 30% 30%, #fff3b0 0%, #ffd700 55%, #f5a623 100%);
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 1px 2px rgba(245, 166, 35, 0.5);
    z-index: 12;
    pointer-events: none;
  }

  // 流苏绳子：从扣子中心垂下
  .tassel-string {
    position: absolute;
    top: 16px;   // 扣子底部
    left: 44px;  // 扣子中心
    width: 2px;
    height: 12px;
    background: linear-gradient(180deg, #ffd700 0%, #f5a623 100%);
    border-radius: 1px;
    box-shadow: 0 1px 2px rgba(245, 166, 35, 0.35);
    z-index: 11;
    pointer-events: none;
  }

  // 流苏穗：从绳子底部散开
  .tassel-ball {
    position: absolute;
    top: 27px;   // 绳子底部
    left: 42px;  // 对准绳子中心
    width: 5px;
    height: 6px;
    z-index: 11;
    pointer-events: none;
    
    // 用渐变模拟紧凑的流苏穗效果
    background: linear-gradient(
      to bottom,
      rgba(255, 215, 0, 0.9) 0%,
      rgba(245, 166, 35, 0.85) 30%,
      rgba(255, 215, 0, 0.75) 60%,
      rgba(245, 166, 35, 0.6) 85%,
      transparent 100%
    );
    border-radius: 0 0 40% 40%;
    filter: blur(0.2px);
    
    // 用 box-shadow 增加层次感
    box-shadow: 
      0 1px 0 rgba(255, 215, 0, 0.4),
      0 2px 0 rgba(245, 166, 35, 0.3);
  }
  
  // 帽子底座（连接头部）
  .cap-base {
    width: 16px;
    height: 8px;
    background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
    margin: -6px auto 0;
    border-radius: 2px 2px 4px 4px;
    position: relative;
    z-index: 1;
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
.ear {
  position: absolute;
  width: 10px;
  height: 16px;
  background: linear-gradient(180deg, #79bbff 0%, #409eff 100%);
  border-radius: 5px;
  top: 12px;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
  
  &::after {
    content: '';
    position: absolute;
    top: 3px;
    width: 4px;
    height: 8px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
  }
  
  &.ear-left {
    left: -4px;
    &::after { left: 2px; }
  }
  
  &.ear-right {
    right: -4px;
    &::after { right: 2px; }
  }
}

// 头部
.head {
  width: 52px;
  height: 48px;
  background: linear-gradient(180deg, #a0d2ff 0%, #79bbff 30%, #409eff 100%);
  border-radius: 16px 16px 20px 20px;
  position: relative;
  box-shadow: 
    0 6px 16px rgba(64, 158, 255, 0.35),
    inset 0 2px 8px rgba(255, 255, 255, 0.4),
    inset 0 -2px 6px rgba(64, 158, 255, 0.2);
  overflow: visible;
}

// 面部屏幕
.face-screen {
  position: absolute;
  top: 10px;
  left: 7px;
  right: 7px;
  height: 28px;
  background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
  border-radius: 10px;
  box-shadow: 
    inset 0 2px 6px rgba(0,0,0,0.8),
    0 1px 2px rgba(255,255,255,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 5px;
}

// 眼睛
.eyes {
  display: flex;
  gap: 10px;
  
  .eye {
    width: 12px;
    height: 12px;
    background: radial-gradient(circle at 40% 40%, #fff, #f0f0f0);
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
    position: relative;
    overflow: hidden;
    
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

// 嘴巴
.mouth {
  width: 12px;
  height: 5px;
  background: linear-gradient(180deg, #ff7b7b 0%, #e53935 100%);
  border-radius: 0 0 6px 6px;
  margin-top: 2px;
  box-shadow: 0 1px 3px rgba(229, 57, 53, 0.4);
}

// 眼睛动画
@keyframes look-around {
  0%, 100% { transform: translate(-50%, -50%); }
  25% { transform: translate(-30%, -50%); }
  50% { transform: translate(-50%, -30%); }
  75% { transform: translate(-70%, -50%); }
}

// ========== 其他样式保持不变 ==========
.entry-info {
  .entry-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 6px 0;
    
    .smart-tag {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
    }
  }
  
  .entry-desc {
    font-size: 13px;
    color: #606266;
    margin: 0;
    line-height: 1.5;
  }
}

.entry-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
  
  .action-btn {
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 500;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.25s ease;
    
    .el-icon {
      font-size: 16px;
    }
  }
  
  .primary-btn {
    background: linear-gradient(135deg, #409eff, #337ecc);
    border: none;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
    
    &:hover {
      background: linear-gradient(135deg, #66b1ff, #409eff);
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
    }
  }
  
  .secondary-btn {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(64, 158, 255, 0.3);
    color: #409eff;
    
    &:hover {
      background: #fff;
      border-color: #409eff;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
    }
  }
  
  .history-btn {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(144, 147, 153, 0.3);
    color: #606266;
    
    &:hover:not(:disabled) {
      background: #fff;
      border-color: #909399;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(144, 147, 153, 0.15);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

// 聊天记录抽屉样式
.history-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .history-loading {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #909399;
    
    p {
      margin-top: 12px;
      font-size: 14px;
    }
  }
  
  .history-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #c0c4cc;
    
    p {
      margin-top: 12px;
      font-size: 14px;
    }
    
    .history-tip {
      margin-top: 4px;
      font-size: 12px;
      color: #c0c4cc;
    }
  }
  
  .history-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 4px;
  }
  
  // 会话列表项
  .conversation-item {
    padding: 14px;
    margin-bottom: 10px;
    background: #f5f7fa;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      background: #e8f4fd;
      transform: translateX(4px);
    }
    
    .conv-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 6px;
    }
    
    .conv-title {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .conv-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
      color: #909399;
    }
  }
  
  // 会话详情
  .detail-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding-bottom: 12px;
    margin-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
    
    .detail-title {
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
  
  .history-messages {
    flex: 1;
    overflow-y: auto;
    padding: 0 4px;
  }
  
  .history-item {
    margin-bottom: 16px;
    padding: 12px;
    border-radius: 8px;
    background: #f5f7fa;
    
    &.history-user {
      background: linear-gradient(135deg, #e8f4fd 0%, #d6ecfa 100%);
    }
    
    &.history-assistant {
      background: #f5f7fa;
    }
    
    &.history-error {
      background: rgba(245, 108, 108, 0.1);
    }
  }
  
  .history-role {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    
    .role-tag {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 500;
    }
    
    .user-tag {
      background: #409eff;
      color: #fff;
    }
    
    .assistant-tag {
      background: #67c23a;
      color: #fff;
    }
    
    .history-time {
      font-size: 11px;
      color: #909399;
    }
  }
  
  .history-content {
    font-size: 13px;
    line-height: 1.6;
    color: #303133;
    white-space: pre-wrap;
    word-break: break-word;
  }
  
  .history-footer {
    padding: 12px 0;
    border-top: 1px solid #ebeef5;
    display: flex;
    justify-content: center;
  }
}

.quick-questions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed rgba(64, 158, 255, 0.25);
  
  .quick-header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 500;
    color: #909399;
    margin-bottom: 12px;
    
    .el-icon {
      color: #409eff;
    }
  }
  
  .quick-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    
    .quick-tag {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 8px 14px;
      background: rgba(255, 255, 255, 0.85);
      border: 1px solid rgba(64, 158, 255, 0.2);
      border-radius: 18px;
      font-size: 13px;
      color: #606266;
      cursor: pointer;
      transition: all 0.25s ease;
      
      .el-icon {
        font-size: 12px;
        color: #409eff;
        transition: transform 0.25s ease;
      }
      
      &:hover {
        background: #fff;
        border-color: #409eff;
        color: #409eff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.12);
        
        .el-icon {
          transform: translateX(2px);
        }
      }
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .entry-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .entry-actions {
    width: 100%;
    
    .action-btn {
      flex: 1;
      justify-content: center;
    }
  }
}

// 深色模式
:global(.theme-dark) {
  .ai-assistant-entry {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a3352 50%, #162d47 100%);
    border-color: rgba(64, 158, 255, 0.2);
    
    .entry-info {
      .entry-title {
        color: #f0f0f0;
      }
      
      .entry-desc {
        color: #a0a0a0;
      }
    }
    
    .quick-questions {
      border-top-color: rgba(64, 158, 255, 0.15);
      
      .quick-tag {
        background: rgba(30, 58, 95, 0.8);
        border-color: rgba(64, 158, 255, 0.2);
        color: #c0c0c0;
        
        &:hover {
          background: rgba(40, 78, 125, 0.9);
          color: #66b1ff;
        }
      }
    }
    
    .secondary-btn {
      background: rgba(30, 58, 95, 0.8);
      color: #66b1ff;
      
      &:hover {
        background: rgba(40, 78, 125, 0.9);
      }
    }
  }
}
</style>
