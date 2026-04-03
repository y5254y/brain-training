<template>
  <view class="page-container">
    <view class="game-header card">
      <text class="game-title">🎯 注意力训练</text>
      <text class="game-desc">舒尔特方格 —— 按顺序点击数字，训练注意力与眼球运动</text>
    </view>

    <!-- 难度选择 -->
    <view class="difficulty-section card" v-if="gameState === 'idle'">
      <text class="section-label">选择方格大小</text>
      <!-- 推荐提示（仅登录用户） -->
      <view class="recommend-tip" v-if="recommendLevel !== null">
        <text class="recommend-text">💡 根据你的历史表现，推荐：{{ recommendName }}</text>
      </view>
      <view class="difficulty-row">
        <view
          v-for="d in difficulties"
          :key="d.size"
          class="difficulty-btn"
          :class="{ active: selectedSize === d.size }"
          @click="selectedSize = d.size"
        >
          <text class="d-badge" v-if="d.difficulty === recommendLevel">推荐</text>
          <text class="d-name">{{ d.name }}</text>
          <text class="d-desc">{{ d.size }}×{{ d.size }}</text>
        </view>
      </view>
      <button class="start-btn" @click="startGame">开始游戏</button>
    </view>

    <!-- 预览阶段提示条 -->
    <view class="preview-section card" v-if="gameState === 'preview'">
      <text class="preview-tip">👀 记住数字的位置！</text>
      <text class="preview-countdown">{{ previewCountdown }} 秒后开始</text>
    </view>

    <!-- 游戏区域（preview 与 playing 均显示方格） -->
    <view class="game-area" v-if="gameState === 'playing' || gameState === 'preview'">
      <!-- 游戏信息栏（仅 playing 阶段显示） -->
      <view class="game-info" v-if="gameState === 'playing'">
        <text class="next-hint">找数字：<text class="next-number">{{ nextNumber }}</text></text>
        <text class="timer">⏱ {{ formatTime(timeElapsed) }}</text>
        <text v-if="comboCount >= 3" class="combo-badge">🔥×{{ comboCount }}</text>
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

    <!-- 结果页 -->
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
        <text class="result-stat">⚡ 平均反应时间：{{ avgReactionTime }} 秒/格</text>
        <text class="result-stat" v-if="maxCombo >= 3">🔥 最高连击：{{ maxCombo }}</text>
      </view>
      <view class="result-btns">
        <button class="result-btn retry-btn" @click="resetGame">再玩一次</button>
        <button class="result-btn back-btn" @click="goBack">返回首页</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()

// 游戏状态：idle(等待) / preview(预览倒计时) / playing(游戏中) / finished(结束)
const gameState = ref('idle')
const selectedSize = ref(3)
const cells = ref([])
const nextNumber = ref(1)
const timeElapsed = ref(0)
const errorCount = ref(0)
const score = ref(0)
const previewCountdown = ref(3)
const comboCount = ref(0)
const maxCombo = ref(0)
const comboBonus = ref(0)
const recommendLevel = ref(null)  // null 表示无推荐（未登录/无历史/加载失败）
let timer = null
let previewTimer = null
let inputLocked = false
let cachedAvgSecPerCell = null  // 缓存历史平均每格耗时，用于自适应预览时间

const difficulties = [
  { size: 3, name: '初级', difficulty: 1 },
  { size: 4, name: '中级', difficulty: 2 },
  { size: 5, name: '高级', difficulty: 3 },
]

// difficulty -> grid size 映射
const diffToSize = { 1: 3, 2: 4, 3: 5 }

// 各难度计分配置
const scoreConfig = {
  1: { base: 120, timeFactor: 0.7, errorFactor: 3, completionBonus: 20, perfectBonus: 15, previewBase: 3.0 },
  2: { base: 160, timeFactor: 0.6, errorFactor: 3, completionBonus: 30, perfectBonus: 20, previewBase: 2.5 },
  3: { base: 200, timeFactor: 0.5, errorFactor: 3, completionBonus: 40, perfectBonus: 25, previewBase: 2.0 },
}

// 推荐难度名称
const recommendName = computed(() => {
  const d = difficulties.find((d) => d.difficulty === recommendLevel.value)
  return d ? d.name : ''
})

// 星级评价
const starRating = computed(() => {
  const diff = difficulties.find((d) => d.size === selectedSize.value)
  const config = scoreConfig[diff?.difficulty || 1]
  const maxPossible = config.base + config.completionBonus + config.perfectBonus + 30
  const ratio = score.value / maxPossible
  if (ratio >= 0.75) return 3
  if (ratio >= 0.45) return 2
  return 1
})

// 准确率：正确点击 / 总点击数
const accuracy = computed(() => {
  const total = selectedSize.value * selectedSize.value
  const totalClicks = total + errorCount.value
  if (totalClicks === 0) return 100
  return Math.round((total / totalClicks) * 100)
})

// 平均反应时间（秒/格）
const avgReactionTime = computed(() => {
  const total = selectedSize.value * selectedSize.value
  return (timeElapsed.value / total).toFixed(1)
})

// Fisher-Yates 洗牌算法
const shuffle = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

// 格式化时间
const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// 根据历史表现计算自适应预览时长（秒）
const computePreviewTime = (difficulty) => {
  const base = scoreConfig[difficulty].previewBase
  if (cachedAvgSecPerCell === null) return base
  let extra = 0
  if (cachedAvgSecPerCell >= 1.6) {
    extra = 1.5
  } else if (cachedAvgSecPerCell >= 1.3) {
    extra = 1.0
  } else if (cachedAvgSecPerCell >= 1.1) {
    extra = 0.5
  }
  return Math.min(4.5, base + extra)
}

// 拉取历史记录并计算推荐难度
const loadRecommendation = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const records = await request.get('/training/list', {
      params: { game_type: 'attention', page: 1, page_size: 10 },
    })
    if (!records || records.length === 0) {
      // 无历史：推荐初级，并延长预览时间
      recommendLevel.value = 1
      selectedSize.value = 3
      cachedAvgSecPerCell = 2.0
      return
    }

    // 计算每条记录的每格耗时
    const metrics = records.map((r) => {
      const size = diffToSize[r.difficulty] || 3
      const totalCells = size * size
      return {
        secPerCell: r.duration / totalCells,
        difficulty: r.difficulty,
      }
    })

    const avgSecPerCell = metrics.reduce((s, m) => s + m.secPerCell, 0) / metrics.length
    cachedAvgSecPerCell = avgSecPerCell

    // 最近 3 条趋势
    const recent3 = metrics.slice(0, 3)
    const recent3Bad = recent3.filter((m) => m.secPerCell >= 1.8).length
    const recent3Good = recent3.filter((m) => m.secPerCell <= 0.9).length

    // 当前平均难度
    const avgDiff = Math.round(metrics.reduce((s, m) => s + m.difficulty, 0) / metrics.length)
    const currentDiff = Math.min(3, Math.max(1, avgDiff))

    // 降级：更敏感（中老年保护）
    const shouldDowngrade = recent3Bad >= 2 || avgSecPerCell >= 1.6
    // 升级：更严格
    const shouldUpgrade = recent3Good >= 2 && avgSecPerCell <= 1.0

    let recommended = currentDiff
    if (shouldDowngrade) {
      recommended = Math.max(1, currentDiff - 1)
    } else if (shouldUpgrade) {
      recommended = Math.min(3, currentDiff + 1)
    }

    recommendLevel.value = recommended
    selectedSize.value = diffToSize[recommended]
  } catch (e) {
    console.log('加载历史记录失败', e)
    // 加载失败不影响游戏，不显示推荐
  }
}

// 开始游戏（含预览倒计时）
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
  inputLocked = false

  // 进入预览阶段
  const diff = difficulties.find((d) => d.size === selectedSize.value)
  const previewTime = computePreviewTime(diff?.difficulty || 1)
  previewCountdown.value = Math.ceil(previewTime)
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

// 点击方格
const clickCell = (cell) => {
  if (gameState.value !== 'playing') return
  if (cell.clicked) return
  if (inputLocked) return

  if (cell.value === nextNumber.value) {
    cell.clicked = true
    comboCount.value++
    if (comboCount.value > maxCombo.value) maxCombo.value = comboCount.value
    // 连击奖励
    if (comboCount.value >= 8) {
      comboBonus.value += 12
    } else if (comboCount.value >= 5) {
      comboBonus.value += 8
    } else if (comboCount.value >= 3) {
      comboBonus.value += 5
    }
    nextNumber.value++
    if (nextNumber.value > selectedSize.value * selectedSize.value) {
      finishGame()
    }
  } else {
    // 点错了：闪红 + 锁定 300ms 防连点
    cell.wrong = true
    errorCount.value++
    comboCount.value = 0
    inputLocked = true
    try { uni.vibrateShort({}) } catch (e) { /* 不支持震动的平台忽略即可 */ }
    setTimeout(() => {
      cell.wrong = false
      inputLocked = false
    }, 300)
  }
}

// 游戏结束，计算最终得分
const finishGame = () => {
  clearInterval(timer)
  const diff = difficulties.find((d) => d.size === selectedSize.value)
  const config = scoreConfig[diff?.difficulty || 1]
  const total = selectedSize.value * selectedSize.value

  // 时间惩罚（每格平均耗时 × 系数 × 总格数，平滑封顶）
  const timePenalty = Math.floor((timeElapsed.value / total) * config.timeFactor * total)
  // 错误惩罚（封顶 base 的 40%，避免分数骤降）
  const rawErrorPenalty = errorCount.value * config.errorFactor
  const errorPenalty = Math.min(rawErrorPenalty, Math.floor(config.base * 0.4))
  // 无失误奖励
  const perfectBonus = errorCount.value === 0 ? config.perfectBonus : 0

  score.value = Math.max(
    Math.floor(config.base * 0.1),  // 最低保底分，避免 0 分打击
    Math.round(config.base + config.completionBonus - timePenalty - errorPenalty + perfectBonus + comboBonus.value),
  )

  gameState.value = 'finished'
  submitScore()
}

// 提交成绩（兼容现有后端接口）
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

onMounted(() => { loadRecommendation() })
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
    margin-bottom: 16rpx;
  }

  .recommend-tip {
    background: rgba(74, 144, 226, 0.08);
    border-radius: 12rpx;
    padding: 12rpx 20rpx;
    margin-bottom: 20rpx;

    .recommend-text {
      font-size: 24rpx;
      color: #4a90e2;
    }
  }

  .difficulty-row {
    display: flex;
    gap: 16rpx;
    margin-bottom: 30rpx;

    .difficulty-btn {
      flex: 1;
      border: 2rpx solid #e8e8e8;
      border-radius: 16rpx;
      padding: 20rpx 12rpx;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6rpx;
      position: relative;

      &.active {
        border-color: #4a90e2;
        background: rgba(74, 144, 226, 0.1);
        color: #4a90e2;
      }

      .d-badge {
        font-size: 18rpx;
        background: #4a90e2;
        color: #fff;
        padding: 2rpx 10rpx;
        border-radius: 20rpx;
        line-height: 1.6;
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
      background: linear-gradient(90deg, #ff9a9e, #fecfef);
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

      &.preview {
        background: linear-gradient(135deg, #e8f4fd, #f0f8ff);
        color: #4a90e2;
        cursor: not-allowed;
      }

      &.clicked {
        background: linear-gradient(135deg, #84fab0, #8fd3f4);
        color: #fff;
      }

      &.wrong {
        background: #ff4d4f;
        color: #fff;
        animation: shake 0.3s ease;
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

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8rpx); }
  75% { transform: translateX(8rpx); }
}
</style>
