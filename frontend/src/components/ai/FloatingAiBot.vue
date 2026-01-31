<template>
  <Teleport to="body">
    <div
      v-show="!botHidden"
      class="floating-ai-bot"
      :style="botStyle"
      @pointerdown="handlePointerDown"
      @click="handleClick"
    >
      <!-- 关闭按钮 -->
      <div class="bot-close" @click.stop="handleClose">
        <svg viewBox="0 0 24 24" width="10" height="10" fill="currentColor">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </div>
      
      <!-- 蓝色机器人（与AI助教卡片同款） -->
      <div class="robot-character">
        <!-- 学士帽（菱形样式） -->
        <div class="graduation-cap">
          <div class="cap-top"></div>
          <div class="cap-base"></div>
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
              <div class="eyes">
                <div class="eye eye-left">
                  <div class="pupil"></div>
                </div>
                <div class="eye eye-right">
                  <div class="pupil"></div>
                </div>
              </div>
              <div class="mouth"></div>
            </div>
          </div>
          
            <!-- 身体躯干 -->
            <div class="torso"></div>
            
            <!-- 手臂（圆球手） -->
            <div class="arm arm-left"></div>
            <div class="arm arm-right"></div>
            
            <!-- 脚 -->
            <div class="feet">
              <div class="foot foot-left"></div>
              <div class="foot foot-right"></div>
            </div>
        </div>
      </div>
      
      <!-- 提示气泡 -->
      <transition name="bubble">
        <div v-if="showBubble" class="bot-bubble">
          <span>👋</span> 有问题点我~
        </div>
      </transition>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAiAssistantStore } from '@/stores/aiAssistant'

const store = useAiAssistantStore()
const showBubble = ref(false)

const botHidden = computed(() => store.botHidden)

// 拖拽相关
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const startPosX = ref(0)
const startPosY = ref(0)
const posX = ref(24) // 初始位置 right: 24px
const posY = ref(100) // 初始位置 bottom: 100px
const dragDistance = ref(0)

const DRAG_THRESHOLD = 6 // 拖拽阈值，超过这个距离才算拖拽

// 从 localStorage 恢复位置
onMounted(() => {
  const savedPos = localStorage.getItem('ai_bot_pos_v1')
  if (savedPos) {
    try {
      const pos = JSON.parse(savedPos)
      posX.value = pos.x ?? 24
      posY.value = pos.y ?? 100
    } catch (e) {
      // 忽略解析错误
    }
  }
  
  // 显示欢迎气泡
  setTimeout(() => {
    if (!store.hasMessages) {
      showBubble.value = true
      setTimeout(() => { showBubble.value = false }, 6000)
    }
  }, 1500)
})

// 计算样式
const botStyle = computed(() => ({
  right: `${posX.value}px`,
  bottom: `${posY.value}px`
}))

// 保存位置到 localStorage
const savePosition = () => {
  localStorage.setItem('ai_bot_pos_v1', JSON.stringify({
    x: posX.value,
    y: posY.value
  }))
}

// 拖拽开始
const handlePointerDown = (e) => {
  isDragging.value = true
  dragDistance.value = 0
  dragStartX.value = e.clientX
  dragStartY.value = e.clientY
  startPosX.value = posX.value
  startPosY.value = posY.value
  
  document.addEventListener('pointermove', handlePointerMove)
  document.addEventListener('pointerup', handlePointerUp)
}

// 拖拽中
const handlePointerMove = (e) => {
  if (!isDragging.value) return
  
  const deltaX = dragStartX.value - e.clientX
  const deltaY = dragStartY.value - e.clientY
  dragDistance.value = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
  
  // 计算新位置（从右下角计算）
  let newX = startPosX.value + deltaX
  let newY = startPosY.value + deltaY
  
  // 限制在视口内
  const botWidth = 74
  const botHeight = 95
  const maxX = window.innerWidth - botWidth
  const maxY = window.innerHeight - botHeight
  
  newX = Math.max(0, Math.min(newX, maxX))
  newY = Math.max(0, Math.min(newY, maxY))
  
  posX.value = newX
  posY.value = newY
}

// 拖拽结束
const handlePointerUp = () => {
  document.removeEventListener('pointermove', handlePointerMove)
  document.removeEventListener('pointerup', handlePointerUp)
  
  if (dragDistance.value >= DRAG_THRESHOLD) {
    savePosition()
  }
  
  isDragging.value = false
}

// 点击处理（区分点击和拖拽）
const handleClick = (e) => {
  if (dragDistance.value >= DRAG_THRESHOLD) {
    e.preventDefault()
    e.stopPropagation()
    return
  }
  store.openModal()
}

const handleClose = () => {
  store.hideBot()
}

watch(() => store.hasMessages, (hasMessages) => {
  if (hasMessages) showBubble.value = false
})

onUnmounted(() => {
  document.removeEventListener('pointermove', handlePointerMove)
  document.removeEventListener('pointerup', handlePointerUp)
})
</script>

<style lang="scss" scoped>
.floating-ai-bot {
  position: fixed;
  z-index: 9999;
  width: 74px;
  height: 95px;
  cursor: grab;
  user-select: none;
  touch-action: none;
  transition: transform 0.2s ease;
  
  &:active {
    cursor: grabbing;
  }
  
  &:hover {
    transform: scale(1.05);
    
    .robot-body {
      animation: bounce 0.5s ease;
    }
  }
}

// 关闭按钮
.bot-close {
  position: absolute;
  top: 2px;
  right: 0;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.6);
  transition: all 0.2s ease;
  z-index: 10;
  
  &:hover {
    background: #f56c6c;
    transform: scale(1);
  }
}

.floating-ai-bot:hover .bot-close {
  opacity: 1;
  transform: scale(1);
}

// 机器人角色
.robot-character {
  position: relative;
  width: 100%;
  height: 100%;
}

// 学士帽 - 和上面AI助教卡片完全一样的样式
.graduation-cap {
  position: absolute;
  top: 4px;  // 让帽子底座刚好接到头部顶部
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  overflow: visible;
  width: 50px;
  pointer-events: none;
  
  // 方形帽顶（菱形视角）
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
      box-shadow: 
        0 2px 4px rgba(0,0,0,0.4),
        inset 0 1px 1px rgba(255,255,255,0.1);
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
      opacity: 0.95;
    }
  }

  // 流苏挂点（扣子）
  .tassel-pin {
    position: absolute;
    top: 12px;
    left: 43px;
    width: 4px;
    height: 4px;
    background: radial-gradient(circle at 30% 30%, #fff3b0 0%, #ffd700 55%, #f5a623 100%);
    border-radius: 50%;
    border: 1px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 1px 2px rgba(245, 166, 35, 0.5);
    z-index: 12;
  }

  // 流苏绳子
  .tassel-string {
    position: absolute;
    top: 16px;
    left: 44px;
    width: 2px;
    height: 12px;
    background: linear-gradient(180deg, #ffd700 0%, #f5a623 100%);
    border-radius: 1px;
    box-shadow: 0 1px 2px rgba(245, 166, 35, 0.35);
    z-index: 11;
  }

  // 流苏穗
  .tassel-ball {
    position: absolute;
    top: 27px;
    left: 42px;
    width: 5px;
    height: 6px;
    z-index: 11;
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
    box-shadow: 
      0 1px 0 rgba(255, 215, 0, 0.4),
      0 2px 0 rgba(245, 166, 35, 0.3);
  }
  
  // 帽子底座
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

// 机器人身体部分
.robot-body {
  position: absolute;
  top: 22px;
  left: 50%;
  transform: translateX(-50%);
  width: 64px;
  height: 75px;
}

// 耳朵（蓝色，更圆润）
.ear {
  position: absolute;
  width: 10px;
  height: 14px;
  background: linear-gradient(180deg, #7ec8ff 0%, #52a8ff 50%, #409eff 100%);
  border-radius: 50% 50% 40% 40%;
  top: 12px;
  z-index: 1;
  box-shadow: 
    0 2px 6px rgba(64, 158, 255, 0.4),
    inset 0 1px 3px rgba(255, 255, 255, 0.5);
  
  &.ear-left {
    left: 2px;
  }
  
  &.ear-right {
    right: 2px;
  }
}

// 头部（蓝色，更圆润饱满）
.head {
  position: absolute;
  top: 0;
  left: 8px;
  right: 8px;
  height: 48px;
  background: linear-gradient(180deg, #9ed4ff 0%, #6bb8ff 40%, #409eff 100%);
  border-radius: 50% 50% 45% 45%;
  z-index: 2;
  box-shadow: 
    0 4px 12px rgba(64, 158, 255, 0.4),
    inset 0 3px 10px rgba(255, 255, 255, 0.5),
    inset 0 -3px 8px rgba(64, 158, 255, 0.15);
}

// 面部屏幕（黑色，更圆润）
.face-screen {
  position: absolute;
  top: 10px;
  left: 6px;
  right: 6px;
  height: 28px;
  background: linear-gradient(180deg, #2a2a2a 0%, #1a1a1a 50%, #0d0d0d 100%);
  border-radius: 12px;
  box-shadow: 
    inset 0 2px 6px rgba(0,0,0,0.6),
    inset 0 -1px 2px rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 5px;
}

// 眼睛（更大更可爱）
.eyes {
  display: flex;
  gap: 8px;
  
  .eye {
    width: 12px;
    height: 12px;
    background: radial-gradient(circle at 35% 35%, #fff 0%, #f8f8f8 60%, #e8e8e8 100%);
    border-radius: 50%;
    box-shadow: 
      0 0 6px rgba(255, 255, 255, 0.8),
      inset 0 -1px 2px rgba(0,0,0,0.1);
    position: relative;
    
    .pupil {
      position: absolute;
      width: 4px;
      height: 4px;
      background: radial-gradient(circle at 40% 40%, #444, #111);
      border-radius: 50%;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      
      &::after {
        content: '';
        position: absolute;
        width: 2px;
        height: 2px;
        background: #fff;
        border-radius: 50%;
        top: 0;
        left: 0;
      }
    }
  }
}

// 嘴巴（微笑的弧形）
.mouth {
  width: 12px;
  height: 5px;
  background: linear-gradient(180deg, #ff6b6b 0%, #e84545 100%);
  border-radius: 0 0 50% 50%;
  margin-top: 2px;
  box-shadow: inset 0 1px 2px rgba(255,255,255,0.3);
}

// 身体躯干（圆润的梯形）
.torso {
  position: absolute;
  top: 44px;
  left: 50%;
  transform: translateX(-50%);
  width: 36px;
  height: 22px;
  background: linear-gradient(180deg, #6bb8ff 0%, #52a8ff 50%, #409eff 100%);
  border-radius: 8px 8px 14px 14px;
  z-index: 1;
  box-shadow: 
    0 4px 10px rgba(64, 158, 255, 0.35),
    inset 0 2px 6px rgba(255, 255, 255, 0.35),
    inset 0 -3px 6px rgba(64, 158, 255, 0.2);
  
  // 身体高光
  &::before {
    content: '';
    position: absolute;
    top: 4px;
    left: 50%;
    transform: translateX(-50%);
    width: 20px;
    height: 8px;
    background: rgba(255, 255, 255, 0.25);
    border-radius: 50%;
  }
}

// 手臂（可爱的圆球手）
.arm {
  position: absolute;
  z-index: 2;
  
  &.arm-left, &.arm-right {
    width: 12px;
    height: 12px;
    background: linear-gradient(135deg, #7ec8ff 0%, #52a8ff 60%, #409eff 100%);
    border-radius: 50%;
    top: 50px;
    box-shadow: 
      0 2px 5px rgba(64, 158, 255, 0.4),
      inset 0 1px 3px rgba(255, 255, 255, 0.5);
  }
  
  &.arm-left {
    left: 6px;
  }
  
  &.arm-right {
    right: 6px;
  }
}

// 脚部容器
.feet {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

// 可爱的圆脚
.foot {
  width: 16px;
  height: 12px;
  background: linear-gradient(180deg, #52a8ff 0%, #409eff 60%, #337ecc 100%);
  border-radius: 50% 50% 55% 55%;
  box-shadow: 
    0 3px 6px rgba(64, 158, 255, 0.35),
    inset 0 1px 3px rgba(255, 255, 255, 0.3);
}

// 气泡
.bot-bubble {
  position: absolute;
  right: 78px;
  top: 50%;
  transform: translateY(-50%);
  background: #fff;
  color: #333;
  padding: 10px 16px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border: 1px solid #e4e7ed;
  
  span { margin-right: 4px; }
  
  &::after {
    content: '';
    position: absolute;
    right: -8px;
    top: 50%;
    transform: translateY(-50%);
    border-left: 8px solid #fff;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
  }
}

@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-5px); }
}

.bubble-enter-active,
.bubble-leave-active {
  transition: all 0.3s ease;
}

.bubble-enter-from,
.bubble-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(10px) scale(0.9);
}

:global(.theme-dark) {
  .bot-bubble {
    background: #2d3748;
    color: #e2e8f0;
    border-color: #4a5568;
    
    &::after {
      border-left-color: #2d3748;
    }
  }
}
</style>
