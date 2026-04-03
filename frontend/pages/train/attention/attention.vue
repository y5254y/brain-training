<template>
  <view class="page-container">
    <view class="game-header card">
      <text class="game-title">🎯 注意力训练</text>
      <text class="game-desc">舒尔特方格 —— 按顺序点击数字，训练注意力与眼球运动</text>
    </view>

    <!-- 难度选择 -->
    <view class="difficulty-section card" v-if="gameState === 'idle'">
      <text class="section-label">选择方格大小</text>
      <view class="difficulty-row">
        <view
          v-for="d in difficulties"
          :key="d.size"
          class="difficulty-btn"
          :class="{ active: selectedSize === d.size }"
          @click="selectedSize = d.size"
        >
          <text class="d-name">{{ d.name }}</text>
          <text class="d-desc">{{ d.size }}×{{ d.size }}</text>
        </view>
      </view>
      <button class="start-btn" @click="startGame">开始游戏</button>
    </view>

    <!-- 预览倒计时 -->
    <view class="preview-section card" v-if="gameState === 'preview'">
      <text class="preview-tip">👀 准备开始！</text>
      <text class="preview-countdown">{{ previewCountdown }} 秒后开始</text>
    </view>

    <!-- 游戏区域（预览和游戏中都显示方格） -->
    <view class="game-area" v-if="gameState === 'playing' || gameState === 'preview'">
      <!-- 游戏信息栏（仅游戏中显示） -->
      <view class="game-info" v-if="gameState === 'playing'">
        <text class="next-hint">下一个：<text class="next-number">{{ nextNumber }}</text></text>
        <text v-if="comboCount >= 2" class="combo-badge">🔥×{{ comboCount }}</text>
        <text class="timer">⏱ {{ formatTime(timeElapsed) }}</text>
      </view>

      <view
        class="schulte-grid"
        :style="{ gridTemplateColumns: `repeat(${selectedSize}, 1fr)` }"
      >
        <view
          v-for="(cell, index) in cells"
          :key="index"
          class="schulte-cell"
          :class="{
            clicked: cell.clicked,
            wrong: cell.wrong,
            preview: gameState === 'preview',
          }"
          @click="clickCell(cell)"
        >
          <text>{{ cell.value }}</text>
        </view>
      </view>
    </view>

    <!-- 结果 -->
    <view class="result-section card" v-if="gameState === 'finished'">
      <text class="result-title">🎉 完成！</text>
      <!-- 星级评价 -->
      <view class="stars-row">
        <text
          v-for="n in 3"
          :key="n"
          class="star"
          :class="{ lit: n <= starRating }"
        >★</text>
      </view>
      <text class="result-score">得分：{{ score }}</text>
      <view class="result-stats">
        <text class="result-stat">⏱ 用时：{{ formatTime(timeElapsed) }}</text>
        <text class="result-stat">❌ 错误次数：{{ errorCount }}</text>
        <text class="result-stat">🎯 准确率：{{ accuracy }}%</text>
        <text class="result-stat">⚡ 平均反应：{{ avgReactionTime }}秒/次</text>
        <text class="result-stat">🔥 最高连击：{{ maxCombo }}</text>
      </view>
      <view class="result-btns">
        <button class="result-btn retry-btn" @click="resetGame">再玩一次</button>
        <button class="result-btn back-btn" @click="goBack">返回首页</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()

// 游戏状态：idle(难度选择) / preview(准备) / playing(游戏中) / finished(结束)
const gameState = ref('idle')
const selectedSize = ref(3)
const cells = ref([])
const nextNumber = ref(1)
const timeElapsed = ref(0)
const errorCount = ref(0)
const score = ref(0)
const comboCount = ref(0)
const maxCombo = ref(0)
const comboBonus = ref(0)
const correctClicks = ref(0)
const previewCountdown = ref(3)
let timer = null
let previewTimer = null
let clickLocked = false

const difficulties = [
  { size: 3, name: '初级', difficulty: 1 },
  { size: 4, name: '中级', difficulty: 2 },
  { size: 5, name: '高级', difficulty: 3 },
]

// 难度自适应计分配置
const diffScoreConfig = {
  3: { base: 100, timeFactor: 1.0, errorFactor: 5, noErrorBonus: 10 },
  4: { base: 150, timeFactor: 0.9, errorFactor: 6, noErrorBonus: 20 },
  5: { base: 200, timeFactor: 0.8, errorFactor: 7, noErrorBonus: 30 },
}

// 星级评价
const starRating = computed(() => {
  const config = diffScoreConfig[selectedSize.value]
  const ratio = score.value / config.base
  if (ratio >= 0.8) return 3
  if (ratio >= 0.5) return 2
  return 1
})

// 准确率
const accuracy = computed(() => {
  const total = correctClicks.value + errorCount.value
  if (total === 0) return 100
  return Math.round((correctClicks.value / total) * 100)
})

// 平均反应时间（秒/次，保留1位小数）
const avgReactionTime = computed(() => {
  if (correctClicks.value === 0) return '0.0'
  return (timeElapsed.value / correctClicks.value).toFixed(1)
})

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// Fisher-Yates 洗牌算法
const shuffle = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

const startGame = () => {
  const total = selectedSize.value * selectedSize.value
  const numbers = shuffle(Array.from({ length: total }, (_, i) => i + 1))
  cells.value = numbers.map((v) => ({ value: v, clicked: false, wrong: false }))
  nextNumber.value = 1
  timeElapsed.value = 0
  errorCount.value = 0
  score.value = 0
  comboCount.value = 0
  maxCombo.value = 0
  comboBonus.value = 0
  correctClicks.value = 0
  clickLocked = false

  // 进入预览状态
  previewCountdown.value = 3
  gameState.value = 'preview'

  previewTimer = setInterval(() => {
    previewCountdown.value--
    if (previewCountdown.value <= 0) {
      clearInterval(previewTimer)
      gameState.value = 'playing'
      timer = setInterval(() => { timeElapsed.value++ }, 1000)
    }
  }, 1000)
}

const clickCell = (cell) => {
  if (gameState.value !== 'playing') return
  if (cell.clicked) return
  if (clickLocked) return

  if (cell.value === nextNumber.value) {
    cell.clicked = true
    correctClicks.value++
    nextNumber.value++
    // 连击
    comboCount.value++
    if (comboCount.value > maxCombo.value) maxCombo.value = comboCount.value
    // 连击奖励
    if (comboCount.value >= 15) {
      comboBonus.value += 5
    } else if (comboCount.value >= 10) {
      comboBonus.value += 3
    } else if (comboCount.value >= 5) {
      comboBonus.value += 2
    }
    try { uni.vibrateShort() } catch (e) { /* 平台不支持时静默忽略 */ }
    if (nextNumber.value > selectedSize.value * selectedSize.value) {
      finishGame()
    }
  } else {
    cell.wrong = true
    errorCount.value++
    comboCount.value = 0
    // 点击锁定 300ms，防止疯狂误点
    clickLocked = true
    try { uni.vibrateShort() } catch (e) { /* 平台不支持时静默忽略 */ }
    setTimeout(() => {
      cell.wrong = false
      clickLocked = false
    }, 300)
  }
}

const finishGame = () => {
  clearInterval(timer)
  const config = diffScoreConfig[selectedSize.value]
  const timePenalty = Math.floor(timeElapsed.value / 5 * config.timeFactor)
  const errorPenalty = errorCount.value * config.errorFactor
  const noErrorBonus = errorCount.value === 0 ? config.noErrorBonus : 0
  score.value = Math.max(0, Math.round(config.base - timePenalty - errorPenalty + noErrorBonus + comboBonus.value))
  gameState.value = 'finished'
  submitScore()
}

const submitScore = async () => {
  if (!userStore.isLoggedIn) return
  const diff = difficulties.find((d) => d.size === selectedSize.value)
  try {
    await request.post('/training/submit', {
      game_type: 'attention',
      score: score.value,
      difficulty: diff?.difficulty || 1,
      duration: timeElapsed.value,
    })
  } catch (e) {
    console.log('提交成绩失败', e)
  }
}

const resetGame = () => {
  clearInterval(timer)
  clearInterval(previewTimer)
  gameState.value = 'idle'
}

const goBack = () => { uni.switchTab({ url: '/pages/index/index' }) }

onUnmounted(() => {
  clearInterval(timer)
  clearInterval(previewTimer)
})
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 24rpx;
}

.game-header {
  background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;

  .game-title {
    display: block;
    font-size: 40rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 10rpx;
  }

  .game-desc {
    display: block;
    font-size: 24rpx;
    color: #555;
  }
}

.difficulty-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;

  .section-label {
    display: block;
    font-size: 30rpx;
    font-weight: bold;
    margin-bottom: 20rpx;
  }

  .difficulty-row {
    display: flex;
    gap: 16rpx;
    margin-bottom: 30rpx;

    .difficulty-btn {
      flex: 1;
      border: 2rpx solid #e8e8e8;
      border-radius: 16rpx;
      padding: 20rpx;
      text-align: center;
      display: flex;
      flex-direction: column;
      gap: 8rpx;

      &.active {
        border-color: #4a90e2;
        background: rgba(74, 144, 226, 0.1);
        color: #4a90e2;
      }

      .d-name { font-size: 28rpx; font-weight: bold; }
      .d-desc { font-size: 22rpx; color: #999; }
    }
  }
}

.start-btn {
  width: 100%;
  height: 90rpx;
  background: linear-gradient(90deg, #a1c4fd, #c2e9fb);
  color: #333;
  font-size: 34rpx;
  font-weight: bold;
  border-radius: 50rpx;
  border: none;
}

.preview-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  text-align: center;

  .preview-tip {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 12rpx;
  }

  .preview-countdown {
    display: block;
    font-size: 48rpx;
    font-weight: bold;
    color: #4a90e2;
  }
}

.game-area {
  .game-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
    border-radius: 16rpx;
    padding: 20rpx 30rpx;
    margin-bottom: 20rpx;

    .next-hint { font-size: 28rpx; color: #555; }
    .next-number { color: #4a90e2; font-weight: bold; font-size: 36rpx; }
    .timer { font-size: 28rpx; color: #555; }

    .combo-badge {
      background: linear-gradient(90deg, #a1c4fd, #c2e9fb);
      color: #333;
      font-weight: bold;
      padding: 4rpx 16rpx;
      border-radius: 20rpx;
      font-size: 24rpx;
    }
  }

  .schulte-grid {
    display: grid;
    gap: 12rpx;

    .schulte-cell {
      aspect-ratio: 1;
      background: #fff;
      border-radius: 12rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40rpx;
      font-weight: bold;
      color: #333;
      box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.08);
      transition: transform 0.15s ease, background 0.2s ease;

      &.preview {
        opacity: 0.85;
      }

      &.clicked {
        background: linear-gradient(135deg, #84fab0, #8fd3f4);
        color: #fff;
        transform: scale(0.95);
      }

      &.wrong {
        background: #ff4d4f;
        color: #fff;
        animation: wrong-shake 0.3s ease;
      }
    }
  }
}

.result-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  text-align: center;

  .result-title {
    display: block;
    font-size: 44rpx;
    font-weight: bold;
    margin-bottom: 16rpx;
  }

  .stars-row {
    display: flex;
    justify-content: center;
    gap: 8rpx;
    margin-bottom: 20rpx;

    .star {
      font-size: 60rpx;
      color: #ddd;

      &.lit {
        color: #f5c518;
      }
    }
  }

  .result-score {
    display: block;
    font-size: 56rpx;
    font-weight: bold;
    color: #4a90e2;
    margin-bottom: 20rpx;
  }

  .result-stats {
    display: flex;
    flex-direction: column;
    gap: 10rpx;
    margin-bottom: 10rpx;

    .result-stat {
      font-size: 28rpx;
      color: #666;
    }
  }

  .result-btns {
    display: flex;
    gap: 20rpx;
    margin-top: 30rpx;

    .result-btn {
      flex: 1;
      height: 88rpx;
      border-radius: 50rpx;
      font-size: 30rpx;
      border: none;
    }

    .retry-btn { background: linear-gradient(90deg, #4a90e2, #7ec8e3); color: #fff; }
    .back-btn { background: #f5f5f5; color: #333; }
  }
}

@keyframes wrong-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-6rpx); }
  75% { transform: translateX(6rpx); }
}
</style>
