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

    <!-- 游戏区域 -->
    <view class="game-area" v-if="gameState === 'playing'">
      <!-- 游戏信息栏 -->
      <view class="game-info">
        <text>⏱ {{ formatTime(timeElapsed) }}</text>
        <text>🔄 翻牌次数: {{ flipCount }}</text>
        <text>✅ 已配对: {{ matchedCount }}/{{ totalPairs }}</text>
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
          :class="{ flipped: card.isFlipped || card.isMatched, matched: card.isMatched }"
          @click="flipCard(index)"
        >
          <view class="card-front">
            <text>{{ card.isFlipped || card.isMatched ? card.emoji : '❓' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 游戏结果 -->
    <view class="result-section card" v-if="gameState === 'finished'">
      <text class="result-title">🎉 游戏完成！</text>
      <text class="result-score">得分：{{ score }}</text>
      <text class="result-time">用时：{{ formatTime(timeElapsed) }}</text>
      <text class="result-flips">翻牌次数：{{ flipCount }}</text>
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

// 游戏状态：idle(等待) / playing(游戏中) / finished(结束)
const gameState = ref('idle')
const selectedDifficulty = ref(1)
const cards = ref([])
const flipCount = ref(0)
const matchedCount = ref(0)
const timeElapsed = ref(0)
const score = ref(0)
let timer = null
let flippedCards = []

// 难度配置
const difficulties = [
  { level: 1, name: '简单', desc: '4×3', rows: 3, cols: 4 },
  { level: 2, name: '中等', desc: '4×4', rows: 4, cols: 4 },
  { level: 3, name: '困难', desc: '4×5', rows: 5, cols: 4 },
]

const currentDifficulty = computed(
  () => difficulties.find((d) => d.level === selectedDifficulty.value) || difficulties[0]
)

const cols = computed(() => currentDifficulty.value.cols)
const totalPairs = computed(() => (currentDifficulty.value.rows * currentDifficulty.value.cols) / 2)

// 表情符号库
const emojiList = ['🍎', '🍊', '🍋', '🍇', '🍓', '🍒', '🍑', '🥝', '🍍', '🥭']

// 格式化时间
const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

// 开始游戏
const startGame = () => {
  const { rows, cols } = currentDifficulty.value
  const pairCount = (rows * cols) / 2
  const selectedEmojis = emojiList.slice(0, pairCount)
  // 创建牌组（每个表情出现两次）并用 Fisher-Yates 算法打乱
  const cardList = [...selectedEmojis, ...selectedEmojis]
  // Fisher-Yates 洗牌算法（均匀随机）
  for (let i = cardList.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[cardList[i], cardList[j]] = [cardList[j], cardList[i]]
  }
  const mappedCards = cardList.map((emoji, index) => ({
    id: index,
    emoji,
    isFlipped: false,
    isMatched: false,
  }))

  cards.value = mappedCards
  flipCount.value = 0
  matchedCount.value = 0
  timeElapsed.value = 0
  score.value = 0
  flippedCards = []
  gameState.value = 'playing'

  // 启动计时器
  timer = setInterval(() => {
    timeElapsed.value++
  }, 1000)
}

// 翻转卡牌
const flipCard = (index) => {
  const card = cards.value[index]
  if (card.isFlipped || card.isMatched || flippedCards.length >= 2) return

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
      flippedCards = []
      // 检查是否全部配对完成
      if (matchedCount.value === totalPairs.value) {
        finishGame()
      }
    } else {
      // 配对失败，延迟翻回
      setTimeout(() => {
        cards.value[i1].isFlipped = false
        cards.value[i2].isFlipped = false
        flippedCards = []
      }, 800)
    }
  }
}

// 游戏结束
const finishGame = () => {
  clearInterval(timer)
  // 计算得分：基础分 - 时间惩罚 - 多余翻牌惩罚
  const baseScore = 100
  const timePenalty = Math.floor(timeElapsed.value / 5)
  const flipPenalty = Math.max(0, flipCount.value - totalPairs.value * 2) * 2
  score.value = Math.max(0, baseScore - timePenalty - flipPenalty)
  gameState.value = 'finished'
  // 提交成绩
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
  gameState.value = 'idle'
}

// 返回首页
const goBack = () => {
  uni.switchTab({ url: '/pages/index/index' })
}

// 页面销毁时清除计时器
onUnmounted(() => {
  clearInterval(timer)
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

.game-area {
  .game-info {
    display: flex;
    justify-content: space-between;
    background: #fff;
    border-radius: 16rpx;
    padding: 20rpx 24rpx;
    margin-bottom: 20rpx;
    font-size: 26rpx;
    color: #555;
  }

  .card-grid {
    display: grid;
    gap: 16rpx;

    .memory-card {
      aspect-ratio: 1;
      background: linear-gradient(135deg, #4a90e2, #7ec8e3);
      border-radius: 16rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.3s;

      &.flipped {
        background: #fff;
        border: 2rpx solid #e8e8e8;
      }

      &.matched {
        background: linear-gradient(135deg, #84fab0, #8fd3f4);
        opacity: 0.8;
      }

      .card-front {
        font-size: 48rpx;
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
    margin-bottom: 20rpx;
  }

  .result-score {
    display: block;
    font-size: 56rpx;
    font-weight: bold;
    color: #4a90e2;
    margin-bottom: 16rpx;
  }

  .result-time,
  .result-flips {
    display: block;
    font-size: 28rpx;
    color: #666;
    margin-bottom: 10rpx;
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
</style>
