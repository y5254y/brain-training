<template>
  <view class="page-container">
    <GameLayout
      title="🧭 空间定向"
      description="记住方向，找到正确的路！"
      headerGradient="linear-gradient(135deg, #667eea, #764ba2)"
      :gameState="gameState"
      :isPractice="isPractice"
      :showModeToggle="true"
      :showDifficulty="true"
      :difficulties="difficulties"
      :selectedDifficulty="selectedDifficulty"
      :recommendedDifficulty="recommendedDiff"
      :score="score"
      :starRating="starRating"
      @update:isPractice="isPractice = $event"
      @update:selectedDifficulty="selectedDifficulty = $event"
      @start="startGame"
      @retry="resetGame"
    >
      <template #info-bar>
        <text>⏱ {{ formatTime(timeElapsed) }}</text>
        <text>📍 第 {{ currentRound }}/{{ totalRounds }} 关</text>
        <text>✅ {{ correctCount }} 对</text>
      </template>

      <view class="spatial-game">
        <view class="direction-display" v-if="gameState === 'preview'">
          <text class="preview-tip">👀 记住这个方向！</text>
          <view class="compass">
            <text class="compass-arrow" :style="{ transform: `rotate(${targetAngle}deg)` }">⬆</text>
            <text class="compass-label">{{ directionLabel }}</text>
          </view>
        </view>

        <view class="direction-question" v-if="gameState === 'playing' && !showingResult">
          <text class="question-text">刚才的方向是？</text>
          <view class="direction-options">
            <view
              v-for="dir in directionOptions"
              :key="dir.angle"
              class="direction-btn"
              :class="{ selected: selectedAngle === dir.angle }"
              @click="selectDirection(dir.angle)"
            >
              <text class="dir-arrow" :style="{ transform: `rotate(${dir.angle}deg)` }">⬆</text>
              <text class="dir-label">{{ dir.label }}</text>
            </view>
          </view>
        </view>
      </view>

      <template #result-stats>
        <view class="result-stats">
          <text class="result-stat">⏱ 用时：{{ formatTime(timeElapsed) }}</text>
          <text class="result-stat">✅ 正确：{{ correctCount }}/{{ totalRounds }}</text>
          <text class="result-stat">🎯 准确率：{{ accuracy }}%</text>
        </view>
      </template>
    </GameLayout>

    <Feedback :type="feedbackType" :visible="showFeedback" />
    <GameGuide
      :visible="showGuide"
      :steps="guideSteps"
      storageKey="guide_spatial"
      @close="showGuide = false"
      @complete="showGuide = false"
    />
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import GameLayout from '@/components/GameLayout.vue'
import Feedback from '@/components/Feedback.vue'
import GameGuide from '@/components/GameGuide.vue'

const userStore = useUserStore()

const gameState = ref('idle')
const isPractice = ref(false)
const selectedDifficulty = ref(1)
const recommendedDiff = ref(null)
const score = ref(0)
const timeElapsed = ref(0)
const currentRound = ref(0)
const correctCount = ref(0)
const targetAngle = ref(0)
const directionLabel = ref('')
const selectedAngle = ref(null)
const directionOptions = ref([])
const showingResult = ref(false)
const showFeedback = ref(false)
const feedbackType = ref('correct')
const showGuide = ref(false)

let timer = null

const difficulties = [
  { level: 1, name: '简单', desc: '4方向' },
  { level: 2, name: '中等', desc: '8方向' },
  { level: 3, name: '困难', desc: '8方向+旋转' },
]

const guideSteps = [
  { icon: '🧭', title: '空间定向训练', desc: '锻炼你的空间感知和方向记忆能力', animation: '🧭' },
  { icon: '👀', title: '记住方向', desc: '屏幕会显示一个方向箭头，仔细记住它指向哪里' },
  { icon: '👆', title: '选择答案', desc: '箭头消失后，从选项中选出正确的方向' },
  { icon: '💪', title: '开始训练', desc: '难度越高，方向越多，还有旋转干扰哦！' },
]

const totalRounds = computed(() => selectedDifficulty.value === 1 ? 8 : 10)
const starRating = computed(() => {
  if (correctCount.value >= totalRounds.value * 0.9) return 3
  if (correctCount.value >= totalRounds.value * 0.7) return 2
  return 1
})
const accuracy = computed(() => {
  if (currentRound.value === 0) return 0
  return Math.round(correctCount.value / currentRound.value * 100)
})

const DIRECTIONS_4 = [
  { angle: 0, label: '北' },
  { angle: 90, label: '东' },
  { angle: 180, label: '南' },
  { angle: 270, label: '西' },
]

const DIRECTIONS_8 = [
  { angle: 0, label: '北' },
  { angle: 45, label: '东北' },
  { angle: 90, label: '东' },
  { angle: 135, label: '东南' },
  { angle: 180, label: '南' },
  { angle: 225, label: '西南' },
  { angle: 270, label: '西' },
  { angle: 315, label: '西北' },
]

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0')
  const s = (seconds % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

const startGame = () => {
  gameState.value = 'preview'
  currentRound.value = 0
  correctCount.value = 0
  timeElapsed.value = 0
  score.value = 0
  nextRound()
}

const nextRound = () => {
  if (currentRound.value >= totalRounds.value) {
    finishGame()
    return
  }

  const dirs = selectedDifficulty.value === 1 ? DIRECTIONS_4 : DIRECTIONS_8
  const target = dirs[Math.floor(Math.random() * dirs.length)]
  targetAngle.value = target.angle
  directionLabel.value = target.label

  const options = [target]
  const otherDirs = dirs.filter(d => d.angle !== target.angle)
  const shuffled = [...otherDirs].sort(() => Math.random() - 0.5)
  options.push(...shuffled.slice(0, 3))
  directionOptions.value = options.sort(() => Math.random() - 0.5)

  selectedAngle.value = null
  showingResult.value = false
  gameState.value = 'preview'

  setTimeout(() => {
    gameState.value = 'playing'
    if (!timer) {
      timer = setInterval(() => { timeElapsed.value++ }, 1000)
    }
  }, selectedDifficulty.value === 1 ? 2000 : 1500)
}

const selectDirection = (angle) => {
  if (showingResult.value) return
  selectedAngle.value = angle
  showingResult.value = true
  currentRound.value++

  const isCorrect = angle === targetAngle.value
  if (isCorrect) {
    correctCount.value++
    feedbackType.value = 'correct'
  } else {
    feedbackType.value = 'wrong'
  }

  showFeedback.value = true
  setTimeout(() => { showFeedback.value = false }, 600)

  setTimeout(() => {
    nextRound()
  }, 1000)
}

const finishGame = () => {
  clearInterval(timer)
  timer = null
  const baseScore = selectedDifficulty.value === 1 ? 60 : selectedDifficulty.value === 2 ? 80 : 100
  score.value = Math.round(baseScore * (correctCount.value / totalRounds.value))
  gameState.value = 'finished'
  submitScore()
}

const submitScore = async () => {
  if (!userStore.isLoggedIn || isPractice.value) return
  try {
    await request.post('/training/submit', {
      game_type: 'spatial',
      score: score.value,
      difficulty: selectedDifficulty.value,
      duration: timeElapsed.value,
      is_practice: isPractice.value ? 1 : 0,
    })
  } catch (e) {
    console.log('提交成绩失败', e)
  }
}

const resetGame = () => {
  clearInterval(timer)
  timer = null
  gameState.value = 'idle'
}

const loadRecommendation = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/training/recommend', { params: { game_type: 'spatial' } })
    recommendedDiff.value = res.recommended_difficulty
  } catch (e) {}
}

onMounted(() => {
  try {
    const guided = uni.getStorageSync('guide_spatial')
    if (!guided) showGuide.value = true
  } catch (e) {}
  loadRecommendation()
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; }

.spatial-game {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.direction-display {
  text-align: center;
  padding: 40rpx;

  .preview-tip {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 30rpx;
  }
}

.compass {
  width: 300rpx;
  height: 300rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: 0 8rpx 30rpx rgba(102, 126, 234, 0.4);

  .compass-arrow {
    font-size: 80rpx;
    color: #fff;
    transition: transform 0.3s ease;
  }

  .compass-label {
    font-size: 28rpx;
    color: rgba(255,255,255,0.9);
    margin-top: 10rpx;
  }
}

.direction-question {
  text-align: center;
  padding: 20rpx;

  .question-text {
    display: block;
    font-size: 34rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 30rpx;
  }
}

.direction-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  max-width: 500rpx;
  margin: 0 auto;
}

.direction-btn {
  background: #fff;
  border: 3rpx solid #e8e8e8;
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;

  &.selected {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.1);
  }

  &:active { transform: scale(0.95); }

  .dir-arrow {
    font-size: 48rpx;
    color: #667eea;
  }

  .dir-label {
    font-size: 26rpx;
    color: #555;
  }
}

.result-stats {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  margin-bottom: 10rpx;

  .result-stat { font-size: 28rpx; color: #666; }
}
</style>
