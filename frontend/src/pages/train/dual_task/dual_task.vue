<template>
  <view class="page-container">
    <GameLayout
      title="🔄 双重任务"
      description="一心二用，同时完成两个任务！"
      headerGradient="linear-gradient(135deg, #fa709a, #fee140)"
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

      <view class="dual-game">
        <view class="dual-tasks" v-if="gameState === 'playing' && !showingResult">
          <view class="task-panel color-task">
            <text class="task-label">🎨 颜色判断</text>
            <text class="task-question">字的颜色是什么？</text>
            <view class="stroop-word" :style="{ color: stroopColor }">{{ stroopText }}</view>
            <view class="color-options">
              <view
                v-for="color in colorOptions"
                :key="color.name"
                class="color-btn"
                :style="{ backgroundColor: color.value }"
                :class="{ selected: selectedColor === color.name }"
                @click="selectColor(color.name)"
              >
                <text class="color-name">{{ color.name }}</text>
              </view>
            </view>
          </view>

          <view class="task-panel math-task">
            <text class="task-label">🔢 快速计算</text>
            <text class="math-question">{{ mathQuestion }}</text>
            <view class="math-options">
              <view
                v-for="opt in mathOptions"
                :key="opt"
                class="math-btn"
                :class="{ selected: selectedMath === opt }"
                @click="selectMath(opt)"
              >
                <text>{{ opt }}</text>
              </view>
            </view>
          </view>
        </view>

        <view class="submit-area" v-if="selectedColor && selectedMath && !showingResult">
          <button class="submit-btn" @click="submitAnswer">确认提交</button>
        </view>
      </view>

      <template #result-stats>
        <view class="result-stats">
          <text class="result-stat">⏱ 用时：{{ formatTime(timeElapsed) }}</text>
          <text class="result-stat">✅ 正确：{{ correctCount }}/{{ totalRounds }}</text>
          <text class="result-stat">🎯 准确率：{{ accuracy }}%</text>
          <text class="result-stat">🎨 颜色正确：{{ colorCorrect }}</text>
          <text class="result-stat">🔢 计算正确：{{ mathCorrect }}</text>
        </view>
      </template>
    </GameLayout>

    <Feedback :type="feedbackType" :visible="showFeedback" />
    <GameGuide
      :visible="showGuide"
      :steps="guideSteps"
      storageKey="guide_dual_task"
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
const colorCorrect = ref(0)
const mathCorrect = ref(0)
const stroopText = ref('')
const stroopColor = ref('')
const selectedColor = ref(null)
const mathQuestion = ref('')
const mathAnswer = ref(0)
const mathOptions = ref([])
const selectedMath = ref(null)
const showingResult = ref(false)
const showFeedback = ref(false)
const feedbackType = ref('correct')
const showGuide = ref(false)

let timer = null

const difficulties = [
  { level: 1, name: '简单', desc: '3色+加减' },
  { level: 2, name: '中等', desc: '4色+乘法' },
  { level: 3, name: '困难', desc: '5色+混合' },
]

const guideSteps = [
  { icon: '🔄', title: '双重任务训练', desc: '锻炼你的注意力分配和多任务处理能力', animation: '🔄' },
  { icon: '🎨', title: '颜色判断', desc: '注意文字显示的颜色（不是文字内容！）' },
  { icon: '🔢', title: '快速计算', desc: '同时完成一道简单的数学计算' },
  { icon: '🧠', title: '一心二用', desc: '两个任务都要答对才算正确！' },
]

const COLORS = [
  { name: '红', value: '#ff4d4f' },
  { name: '蓝', value: '#4a90e2' },
  { name: '绿', value: '#52c41a' },
  { name: '黄', value: '#fadb14' },
  { name: '紫', value: '#722ed1' },
]

const COLOR_NAMES = ['红', '蓝', '绿', '黄', '紫']

const totalRounds = computed(() => 8)
const starRating = computed(() => {
  if (correctCount.value >= totalRounds.value * 0.9) return 3
  if (correctCount.value >= totalRounds.value * 0.7) return 2
  return 1
})
const accuracy = computed(() => {
  if (currentRound.value === 0) return 0
  return Math.round(correctCount.value / currentRound.value * 100)
})

const formatTime = (s) => `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`

const generateStroop = () => {
  const colorCount = selectedDifficulty.value === 1 ? 3 : selectedDifficulty.value === 2 ? 4 : 5
  const available = COLORS.slice(0, colorCount)

  const textColor = available[Math.floor(Math.random() * available.length)]
  let displayText
  do {
    displayText = available[Math.floor(Math.random() * available.length)]
  } while (displayText.name === textColor.name && colorCount > 1)

  stroopText.value = displayText.name
  stroopColor.value = textColor.value
  colorOptions.value = available
  correctColorName.value = textColor.name
}

const generateMath = () => {
  let a, b, op, answer
  if (selectedDifficulty.value === 1) {
    a = Math.floor(Math.random() * 20) + 1
    b = Math.floor(Math.random() * 20) + 1
    op = Math.random() > 0.5 ? '+' : '-'
    if (op === '-' && a < b) [a, b] = [b, a]
    answer = op === '+' ? a + b : a - b
  } else if (selectedDifficulty.value === 2) {
    a = Math.floor(Math.random() * 12) + 2
    b = Math.floor(Math.random() * 9) + 2
    op = '×'
    answer = a * b
  } else {
    const ops = ['+', '-', '×']
    op = ops[Math.floor(Math.random() * ops.length)]
    if (op === '×') {
      a = Math.floor(Math.random() * 12) + 2
      b = Math.floor(Math.random() * 9) + 2
      answer = a * b
    } else {
      a = Math.floor(Math.random() * 50) + 10
      b = Math.floor(Math.random() * 50) + 10
      if (op === '-' && a < b) [a, b] = [b, a]
      answer = op === '+' ? a + b : a - b
    }
  }

  mathQuestion.value = `${a} ${op} ${b} = ?`
  mathAnswer.value = answer

  const options = new Set([answer])
  while (options.size < 4) {
    const offset = Math.floor(Math.random() * 10) - 5
    if (offset !== 0) options.add(answer + offset)
  }
  mathOptions.value = [...options].sort(() => Math.random() - 0.5)
}

const colorOptions = ref([])
const correctColorName = ref('')

const startGame = () => {
  currentRound.value = 0
  correctCount.value = 0
  colorCorrect.value = 0
  mathCorrect.value = 0
  timeElapsed.value = 0
  score.value = 0
  timer = setInterval(() => { timeElapsed.value++ }, 1000)
  nextRound()
}

const nextRound = () => {
  if (currentRound.value >= totalRounds.value) {
    finishGame()
    return
  }
  generateStroop()
  generateMath()
  selectedColor.value = null
  selectedMath.value = null
  showingResult.value = false
  gameState.value = 'playing'
}

const selectColor = (name) => { selectedColor.value = name }
const selectMath = (opt) => { selectedMath.value = opt }

const submitAnswer = () => {
  if (!selectedColor.value || selectedMath.value === null) return
  showingResult.value = true
  currentRound.value++

  const colorOk = selectedColor.value === correctColorName.value
  const mathOk = selectedMath.value === mathAnswer.value

  if (colorOk) colorCorrect.value++
  if (mathOk) mathCorrect.value++

  if (colorOk && mathOk) {
    correctCount.value++
    feedbackType.value = 'correct'
  } else {
    feedbackType.value = 'wrong'
  }

  showFeedback.value = true
  setTimeout(() => { showFeedback.value = false }, 600)

  setTimeout(() => { nextRound() }, 1200)
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
      game_type: 'dual_task',
      score: score.value,
      difficulty: selectedDifficulty.value,
      duration: timeElapsed.value,
      is_practice: isPractice.value ? 1 : 0,
    })
  } catch (e) {}
}

const resetGame = () => {
  clearInterval(timer)
  timer = null
  gameState.value = 'idle'
}

const loadRecommendation = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/training/recommend', { params: { game_type: 'dual_task' } })
    recommendedDiff.value = res.recommended_difficulty
  } catch (e) {}
}

onMounted(() => {
  try { const g = uni.getStorageSync('guide_dual_task'); if (!g) showGuide.value = true } catch(e) {}
  loadRecommendation()
})

onUnmounted(() => { clearInterval(timer) })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; }

.dual-game { padding: 0 24rpx; }

.dual-tasks {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.task-panel {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;

  .task-label {
    display: block;
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 12rpx;
  }

  .task-question {
    display: block;
    font-size: 24rpx;
    color: #666;
    margin-bottom: 16rpx;
  }
}

.stroop-word {
  font-size: 64rpx;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20rpx;
}

.color-options {
  display: flex;
  gap: 12rpx;
  justify-content: center;
  flex-wrap: wrap;
}

.color-btn {
  width: 100rpx;
  height: 80rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3rpx solid transparent;

  &.selected {
    border-color: #333;
    transform: scale(1.1);
  }

  .color-name { font-size: 24rpx; color: #fff; font-weight: bold; text-shadow: 0 1rpx 4rpx rgba(0,0,0,0.3); }
}

.math-question {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 20rpx;
}

.math-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12rpx;
}

.math-btn {
  background: #f5f5f5;
  border-radius: 16rpx;
  padding: 20rpx;
  text-align: center;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;

  &.selected {
    background: rgba(250, 112, 154, 0.15);
    border: 2rpx solid #fa709a;
  }

  &:active { transform: scale(0.95); }
}

.submit-area {
  margin-top: 24rpx;
  .submit-btn {
    width: 100%;
    height: 88rpx;
    background: linear-gradient(135deg, #fa709a, #fee140);
    color: #333;
    font-size: 32rpx;
    font-weight: bold;
    border-radius: 50rpx;
    border: none;
  }
}

.result-stats {
  display: flex; flex-direction: column; gap: 10rpx;
  .result-stat { font-size: 28rpx; color: #666; }
}
</style>
