<template>
  <view class="page-container">
    <view class="game-header card">
      <text class="game-title">🔢 计算力训练</text>
      <text class="game-desc">快速心算，训练你的数学计算能力！</text>
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
          <text class="d-name">{{ d.name }}</text>
          <text class="d-desc">{{ d.desc }}</text>
        </view>
      </view>
      <button class="start-btn" @click="startGame">开始游戏</button>
    </view>

    <!-- 游戏区域 -->
    <view class="game-area card" v-if="gameState === 'playing'">
      <view class="progress-info">
        <text>第 {{ currentQuestion }}/{{ totalQuestions }} 题</text>
        <text class="timer">⏱ {{ timeLeft }}s</text>
        <text>✅ {{ correctCount }} 正确</text>
      </view>

      <!-- 进度条 -->
      <view class="progress-bar">
        <view
          class="progress-fill"
          :style="{ width: `${(timeLeft / questionTime) * 100}%` }"
        ></view>
      </view>

      <!-- 题目 -->
      <view class="question-area">
        <text class="question-text">{{ question }}</text>
      </view>

      <!-- 选项 -->
      <view class="options-grid">
        <view
          v-for="(option, index) in options"
          :key="index"
          class="option-btn"
          :class="{
            correct: answerResult === 'correct' && option === correctAnswer,
            wrong: answerResult === 'wrong' && option === selectedOption,
          }"
          @click="selectAnswer(option)"
        >
          <text>{{ option }}</text>
        </view>
      </view>
    </view>

    <!-- 结果 -->
    <view class="result-section card" v-if="gameState === 'finished'">
      <text class="result-title">🎉 答题完成！</text>
      <text class="result-score">得分：{{ score }}</text>
      <text class="result-correct">正确：{{ correctCount }}/{{ totalQuestions }}</text>
      <view class="result-btns">
        <button class="result-btn retry-btn" @click="resetGame">再玩一次</button>
        <button class="result-btn back-btn" @click="goBack">返回首页</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()

const gameState = ref('idle')
const selectedDifficulty = ref(1)
const currentQuestion = ref(0)
const totalQuestions = 10
const correctCount = ref(0)
const question = ref('')
const options = ref([])
const correctAnswer = ref(0)
const selectedOption = ref(null)
const answerResult = ref('')
const score = ref(0)
const timeLeft = ref(0)
const questionTime = ref(10)
const startTime = ref(0)
let timer = null

const difficulties = [
  { level: 1, name: '简单', desc: '两位数加减', maxNum: 20, ops: ['+', '-'] },
  { level: 2, name: '中等', desc: '三位数加减乘', maxNum: 100, ops: ['+', '-', '×'] },
  { level: 3, name: '困难', desc: '混合运算', maxNum: 200, ops: ['+', '-', '×', '÷'] },
]

const getOperands = (level) => {
  const d = difficulties.find((d) => d.level === level) || difficulties[0]
  const a = Math.floor(Math.random() * d.maxNum) + 1
  const b = Math.floor(Math.random() * (d.maxNum / 2)) + 1
  const op = d.ops[Math.floor(Math.random() * d.ops.length)]
  let result
  let q
  if (op === '+') { result = a + b; q = `${a} + ${b} = ?` }
  else if (op === '-') { result = a - b; q = `${Math.max(a, b)} - ${Math.min(a, b)} = ?`; }
  else if (op === '×') { const x = Math.min(a, 12); const y = Math.min(b, 12); result = x * y; q = `${x} × ${y} = ?` }
  else { const divisor = Math.min(b, 10) || 1; result = Math.floor(a / divisor) * divisor / divisor; q = `${Math.floor(a / divisor) * divisor} ÷ ${divisor} = ?` }
  return { question: q, answer: Math.abs(result) }
}

const generateOptions = (answer) => {
  const opts = new Set([answer])
  while (opts.size < 4) {
    const offset = Math.floor(Math.random() * 10) - 5
    if (offset !== 0) opts.add(Math.abs(answer + offset))
  }
  return [...opts].sort(() => Math.random() - 0.5)
}

const startGame = () => {
  currentQuestion.value = 0
  correctCount.value = 0
  score.value = 0
  startTime.value = Date.now()
  const d = difficulties.find((d) => d.level === selectedDifficulty.value)
  questionTime.value = d?.level === 1 ? 10 : d?.level === 2 ? 8 : 6
  gameState.value = 'playing'
  nextQuestion()
}

const nextQuestion = () => {
  if (currentQuestion.value >= totalQuestions) {
    finishGame()
    return
  }
  currentQuestion.value++
  const { question: q, answer } = getOperands(selectedDifficulty.value)
  question.value = q
  correctAnswer.value = answer
  options.value = generateOptions(answer)
  selectedOption.value = null
  answerResult.value = ''
  timeLeft.value = questionTime.value
  clearInterval(timer)
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      answerResult.value = 'timeout'
      setTimeout(nextQuestion, 600)
    }
  }, 1000)
}

const selectAnswer = (option) => {
  if (answerResult.value) return
  clearInterval(timer)
  selectedOption.value = option
  if (option === correctAnswer.value) {
    answerResult.value = 'correct'
    correctCount.value++
  } else {
    answerResult.value = 'wrong'
  }
  setTimeout(nextQuestion, 600)
}

const finishGame = () => {
  const totalTime = Math.floor((Date.now() - startTime.value) / 1000)
  score.value = Math.round((correctCount.value / totalQuestions) * 100)
  gameState.value = 'finished'
  submitScore(totalTime)
}

const submitScore = async (duration) => {
  if (!userStore.isLoggedIn) return
  try {
    await request.post('/training/submit', {
      game_type: 'calculation',
      score: score.value,
      difficulty: selectedDifficulty.value,
      duration,
    })
  } catch (e) {
    console.log('提交成绩失败', e)
  }
}

const resetGame = () => { gameState.value = 'idle' }
const goBack = () => { uni.switchTab({ url: '/pages/index/index' }) }

onUnmounted(() => { clearInterval(timer) })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 24rpx; }

.game-header {
  background: linear-gradient(135deg, #84fab0, #8fd3f4);
  border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .game-title { display: block; font-size: 40rpx; font-weight: bold; color: #333; margin-bottom: 10rpx; }
  .game-desc { display: block; font-size: 24rpx; color: #555; }
}

.difficulty-section {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .section-label { display: block; font-size: 30rpx; font-weight: bold; margin-bottom: 20rpx; }
  .difficulty-row { display: flex; gap: 16rpx; margin-bottom: 30rpx; }
  .difficulty-btn {
    flex: 1; border: 2rpx solid #e8e8e8; border-radius: 16rpx; padding: 20rpx;
    text-align: center; display: flex; flex-direction: column; gap: 8rpx;
    &.active { border-color: #4a90e2; background: rgba(74,144,226,0.1); color: #4a90e2; }
    .d-name { font-size: 28rpx; font-weight: bold; }
    .d-desc { font-size: 22rpx; color: #999; }
  }
}

.start-btn {
  width: 100%; height: 90rpx;
  background: linear-gradient(90deg, #84fab0, #8fd3f4);
  color: #333; font-size: 34rpx; font-weight: bold; border-radius: 50rpx; border: none;
}

.game-area {
  background: #fff; border-radius: 20rpx; padding: 30rpx;
  .progress-info { display: flex; justify-content: space-between; font-size: 26rpx; color: #555; margin-bottom: 16rpx; }
  .timer { color: #ff4d4f; font-weight: bold; }
  .progress-bar { height: 12rpx; background: #f0f0f0; border-radius: 6rpx; margin-bottom: 40rpx; overflow: hidden; }
  .progress-fill { height: 100%; background: linear-gradient(90deg, #84fab0, #4a90e2); border-radius: 6rpx; transition: width 1s linear; }
  .question-area { text-align: center; margin-bottom: 40rpx; }
  .question-text { font-size: 64rpx; font-weight: bold; color: #333; }
  .options-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20rpx; }
  .option-btn {
    background: #f5f5f5; border-radius: 16rpx; padding: 30rpx; text-align: center;
    font-size: 40rpx; font-weight: bold; color: #333;
    &.correct { background: #52c41a; color: #fff; }
    &.wrong { background: #ff4d4f; color: #fff; }
    &:active { opacity: 0.8; }
  }
}

.result-section {
  background: #fff; border-radius: 20rpx; padding: 40rpx; text-align: center;
  .result-title { display: block; font-size: 44rpx; font-weight: bold; margin-bottom: 20rpx; }
  .result-score { display: block; font-size: 56rpx; font-weight: bold; color: #4a90e2; margin-bottom: 16rpx; }
  .result-correct { display: block; font-size: 28rpx; color: #666; margin-bottom: 10rpx; }
  .result-btns { display: flex; gap: 20rpx; margin-top: 30rpx; }
  .result-btn { flex: 1; height: 88rpx; border-radius: 50rpx; font-size: 30rpx; border: none; }
  .retry-btn { background: linear-gradient(90deg, #4a90e2, #7ec8e3); color: #fff; }
  .back-btn { background: #f5f5f5; color: #333; }
}
</style>
