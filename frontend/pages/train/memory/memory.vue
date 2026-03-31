<template>
  <view class="page-container">
    <view class="game-header card">
      <text class="game-title">🃏 记忆力训练</text>
      <text class="game-desc">翻开两张相同的牌，考验你的记忆力！</text>
    </view>

    <!-- 难度选择 -->
    <view class="difficulty-section card" v-if="gameState === 'idle'">
      <text class="section-label">选择难度</text>
      <view class="difficulty-row">
        <view
          v-for="d in difficulties"
          :key="d.level"
          class="difficulty-btn"
          :class="{ active: selectedDifficulty === d.level }"
          @click="selectedDifficulty = d.level"
        >
          <text>{{ d.name }}</text>
          <text class="diff-desc">{{ d.desc }}</text>
        </view>
      </view>
      <button class="start-btn" @click="startGame">开始游戏</button>
    </view>

    <!-- 预览倒计时 -->
    <view class="preview-section card" v-if="gameState === 'preview'">
      <text class="preview-tip">👀 记住这些位置！</text>
      <text class="preview-countdown">{{ previewCountdown }} 秒后开始</text>
    </view>

    <!-- 游戏区域 -->
    <view class="game-area" v-if="gameState === 'playing' || gameState === 'preview'">
      <!-- 游戏信息栏 -->
      <view class="game-info" v-if="gameState === 'playing'">
        <text>⏱ {{ formatTime(timeElapsed) }}</text>
        <text>🔄 翻牌: {{ flipCount }}</text>
        <text>✅ {{ matchedCount }}/{{ totalPairs }}</text>
        <text v-if="comboCount >= 2" class="combo-badge">🔥×{{ comboCount }}</text>
      </view>

      <!-- 翻牌网格 -->
      <view
        class="card-grid"
        :style="{ gridTemplateColumns: `repeat(${cols}, 1fr)` }"
      >
        <view
          v-for="(card, index) in cards"
          :key="index"
          class="memory-card"
          :class="{
            flipped: card.isFlipped || card.isMatched,
            matched: card.isMatched,
            shake: card.isShaking,
          }"
          @click="flipCard(index)"
        >
          <view class="card-inner">
            <view class="card-back">❓</view>
            <view class="card-front">{{ card.emoji }}</view>
          </view>
        </view>
      </view>
    </view>

    <!-- 游戏结果 -->
    <view class="result-section card" v-if="gameState === 'finished'">
      <text class="result-title">🎉 游戏完成！</text>
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
        <text class="result-stat">🔄 翻牌：{{ flipCount }} 次</text>
        <text class="result-stat">🎯 准确率：{{ accuracy }}%</text>
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

// 游戏状态：idle(等待) / preview(预览) / playing(游戏中) / finished(结束)
const gameState = ref('idle')
const selectedDifficulty = ref(1)
const cards = ref([])
const flipCount = ref(0)
const matchedCount = ref(0)
const timeElapsed = ref(0)
const score = ref(0)
const comboCount = ref(0)
const maxCombo = ref(0)
const comboBonus = ref(0)
const previewCountdown = ref(3)
let timer = null
let previewTimer = null
let flippedCards = []

// 难度配置
const difficulties = [
  { level: 1, name: '简单', desc: '4×3', rows: 3, cols: 4 },
  { level: 2, name: '中等', desc: '4×4', rows: 4, cols: 4 },
  { level: 3, name: '困难', desc: '4×5', rows: 5, cols: 4 },
]

// 难度计分配置
const diffScoreConfig = {
  1: { base: 100, timeFactor: 1, flipFactor: 2, previewTime: 3 },
  2: { base: 150, timeFactor: 0.8, flipFactor: 1.5, previewTime: 2.5 },
  3: { base: 200, timeFactor: 0.6, flipFactor: 1, previewTime: 2 },
}

const currentDifficulty = computed(
  () => difficulties.find((d) => d.level === selectedDifficulty.value) || difficulties[0]
)

const cols = computed(() => currentDifficulty.value.cols)
const totalPairs = computed(() => (currentDifficulty.value.rows * currentDifficulty.value.cols) / 2)

// 星级评价
const starRating = computed(() => {
  const config = diffScoreConfig[selectedDifficulty.value]
  const ratio = score.value / config.base
  if (ratio >= 0.8) return 3
  if (ratio >= 0.5) return 2
  return 1
})

// 准确率
const accuracy = computed(() => {
  if (flipCount.value === 0) return 100
  return Math.round((matchedCount.value * 2) / flipCount.value * 100)
})

// 扩充后的 Emoji 库（20个，多种类别）
const emojiList = [
  '🍎', '🍊', '🍋', '🍇', '🍓', '🍒', '🍑', '🥝', '🍍', '🥭',
  '🐶', '🐱', '🐼', '🦊', '🐸', '🦋', '🌟', '🌈', '🔥', '🎵',
]

// 格式化时间
const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// 开始游戏（含预览）
const startGame = () => {
  const { rows, cols: numCols } = currentDifficulty.value
  const pairCount = (rows * numCols) / 2
  const selectedEmojis = emojiList.slice(0, pairCount)
  // 创建牌组并用 Fisher-Yates 算法打乱
  const cardList = [...selectedEmojis, ...selectedEmojis]
  for (let i = cardList.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[cardList[i], cardList[j]] = [cardList[j], cardList[i]]
  }
  const mappedCards = cardList.map((emoji, index) => ({
    id: index,
    emoji,
    isFlipped: true,   // 预览时全部翻开
    isMatched: false,
    isShaking: false,
  }))

  cards.value = mappedCards
  flipCount.value = 0
  matchedCount.value = 0
  timeElapsed.value = 0
  score.value = 0
  comboCount.value = 0
  maxCombo.value = 0
  comboBonus.value = 0
  flippedCards = []

  // 进入预览状态
  const config = diffScoreConfig[selectedDifficulty.value]
  previewCountdown.value = Math.ceil(config.previewTime)
  gameState.value = 'preview'

  // 每秒倒计时
  previewTimer = setInterval(() => {
    previewCountdown.value--
    if (previewCountdown.value <= 0) {
      clearInterval(previewTimer)
      // 翻回所有牌，开始游戏
      cards.value.forEach((card) => {
        card.isFlipped = false
      })
      gameState.value = 'playing'
      timer = setInterval(() => {
        timeElapsed.value++
      }, 1000)
    }
  }, 1000)
}

// 翻转卡牌
const flipCard = (index) => {
  if (gameState.value !== 'playing') return
  const card = cards.value[index]
  // 防止重复点击同一张牌或已翻开/匹配的牌
  if (card.isFlipped || card.isMatched || flippedCards.length >= 2) return
  if (flippedCards.includes(index)) return

  card.isFlipped = true
  flippedCards.push(index)
  flipCount.value++

  if (flippedCards.length === 2) {
    const [i1, i2] = flippedCards
    if (cards.value[i1].emoji === cards.value[i2].emoji) {
      // 配对成功
      cards.value[i1].isMatched = true
      cards.value[i2].isMatched = true
      matchedCount.value++
      // 连击奖励
      comboCount.value++
      if (comboCount.value > maxCombo.value) maxCombo.value = comboCount.value
      if (comboCount.value >= 4) {
        comboBonus.value += 15
      } else if (comboCount.value === 3) {
        comboBonus.value += 10
      } else if (comboCount.value === 2) {
        comboBonus.value += 5
      }
      flippedCards = []
      // 检查是否全部配对完成
      if (matchedCount.value === totalPairs.value) {
        finishGame()
      }
    } else {
      // 配对失败，抖动动画后翻回
      comboCount.value = 0
      cards.value[i1].isShaking = true
      cards.value[i2].isShaking = true
      setTimeout(() => {
        cards.value[i1].isFlipped = false
        cards.value[i2].isFlipped = false
        cards.value[i1].isShaking = false
        cards.value[i2].isShaking = false
        flippedCards = []
      }, 800)
    }
  }
}

// 游戏结束
const finishGame = () => {
  clearInterval(timer)
  const config = diffScoreConfig[selectedDifficulty.value]
  const timePenalty = Math.floor(timeElapsed.value / 5 * config.timeFactor)
  const flipPenalty = Math.max(0, flipCount.value - totalPairs.value * 2) * config.flipFactor
  score.value = Math.max(0, Math.round(config.base - timePenalty - flipPenalty + comboBonus.value))
  gameState.value = 'finished'
  submitScore()
}

// 提交成绩到后端
const submitScore = async () => {
  if (!userStore.isLoggedIn) return
  try {
    await request.post('/training/submit', {
      game_type: 'memory',
      score: score.value,
      difficulty: selectedDifficulty.value,
      duration: timeElapsed.value,
    })
  } catch (e) {
    console.log('提交成绩失败', e)
  }
}

// 重置游戏
const resetGame = () => {
  clearInterval(timer)
  clearInterval(previewTimer)
  gameState.value = 'idle'
}

// 返回首页
const goBack = () => {
  uni.switchTab({ url: '/pages/index/index' })
}

// 页面销毁时清除计时器
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
  background: linear-gradient(135deg, #ff9a9e, #fecfef);
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
    font-size: 26rpx;
    color: #666;
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
    color: #333;
    margin-bottom: 20rpx;
  }

  .difficulty-row {
    display: flex;
    gap: 16rpx;
    margin-bottom: 30rpx;
  }

  .difficulty-btn {
    flex: 1;
    border: 2rpx solid #e8e8e8;
    border-radius: 16rpx;
    padding: 20rpx 12rpx;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 8rpx;

    &.active {
      border-color: #4a90e2;
      background: rgba(74, 144, 226, 0.1);
      color: #4a90e2;
    }

    .diff-desc {
      font-size: 22rpx;
      color: #999;
    }
  }
}

.start-btn {
  width: 100%;
  height: 90rpx;
  background: linear-gradient(90deg, #ff9a9e, #fecfef);
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
    color: #ff9a9e;
  }
}

.game-area {
  .game-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
    border-radius: 16rpx;
    padding: 20rpx 24rpx;
    margin-bottom: 20rpx;
    font-size: 26rpx;
    color: #555;

    .combo-badge {
      background: linear-gradient(90deg, #ff9a9e, #fecfef);
      color: #333;
      font-weight: bold;
      padding: 4rpx 16rpx;
      border-radius: 20rpx;
      font-size: 24rpx;
    }
  }

  .card-grid {
    display: grid;
    gap: 16rpx;

    .memory-card {
      aspect-ratio: 1;
      perspective: 600px;
      cursor: pointer;

      .card-inner {
        width: 100%;
        height: 100%;
        position: relative;
        transform-style: preserve-3d;
        transition: transform 0.4s ease;
        border-radius: 16rpx;
      }

      .card-back,
      .card-front {
        position: absolute;
        inset: 0;
        border-radius: 16rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48rpx;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
      }

      .card-back {
        background: linear-gradient(135deg, #4a90e2, #7ec8e3);
      }

      .card-front {
        background: #fff;
        border: 2rpx solid #e8e8e8;
        transform: rotateY(180deg);
      }

      &.flipped .card-inner {
        transform: rotateY(180deg);
      }

      &.matched .card-inner {
        transform: rotateY(180deg);
        animation: matched-bounce 0.4s ease;
      }

      &.matched .card-front {
        background: linear-gradient(135deg, #84fab0, #8fd3f4);
        border-color: transparent;
      }

      &.shake {
        animation: shake 0.5s ease;
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

    .retry-btn {
      background: linear-gradient(90deg, #4a90e2, #7ec8e3);
      color: #fff;
    }

    .back-btn {
      background: #f5f5f5;
      color: #333;
    }
  }
}

@keyframes matched-bounce {
  0% { transform: rotateY(180deg) scale(1); }
  40% { transform: rotateY(180deg) scale(1.15); }
  70% { transform: rotateY(180deg) scale(0.95); }
  100% { transform: rotateY(180deg) scale(1); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-8rpx); }
  40% { transform: translateX(8rpx); }
  60% { transform: translateX(-6rpx); }
  80% { transform: translateX(6rpx); }
}
</style>
