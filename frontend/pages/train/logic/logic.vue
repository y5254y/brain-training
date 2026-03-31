<template>
  <view class="page-container">
    <view class="game-header card">
      <text class="game-title">🧩 逻辑推理</text>
      <text class="game-desc">找出数列规律，训练逻辑思维能力！</text>
    </view>

    <!-- 题目区域 -->
    <view class="quiz-section card" v-if="gameState === 'playing'">
      <view class="quiz-progress">
        <text>第 {{ currentIndex + 1 }}/{{ questions.length }} 题</text>
        <text>得分：{{ score }}</text>
      </view>

      <view class="quiz-question">
        <text class="question-label">找出下一个数字：</text>
        <view class="sequence-row">
          <text
            v-for="(num, i) in currentQuestion.sequence"
            :key="i"
            class="seq-num"
          >{{ num }}</text>
          <text class="seq-num unknown">?</text>
        </view>
      </view>

      <!-- 选项 -->
      <view class="options-grid">
        <view
          v-for="(opt, i) in currentQuestion.options"
          :key="i"
          class="option-btn"
          :class="{
            correct: answered && opt === currentQuestion.answer,
            wrong: answered && opt === selectedOption && opt !== currentQuestion.answer,
          }"
          @click="selectOption(opt)"
        >
          <text>{{ opt }}</text>
        </view>
      </view>

      <text class="hint-text" v-if="answered">
        {{ selectedOption === currentQuestion.answer ? '✅ 正确！' : `❌ 正确答案是 ${currentQuestion.answer}` }}
      </text>
    </view>

    <!-- 开始 -->
    <view class="start-section card" v-if="gameState === 'idle'">
      <text class="start-desc">共 {{ questions.length }} 道数列推理题，找出规律填写缺失的数字</text>
      <button class="start-btn" @click="startGame">开始挑战</button>
    </view>

    <!-- 结果 -->
    <view class="result-section card" v-if="gameState === 'finished'">
      <text class="result-title">🎉 挑战完成！</text>
      <text class="result-score">得分：{{ score }}</text>
      <text class="result-correct">正确：{{ correctCount }}/{{ questions.length }}</text>
      <view class="result-btns">
        <button class="result-btn retry-btn" @click="resetGame">再做一次</button>
        <button class="result-btn back-btn" @click="goBack">返回首页</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()

const gameState = ref('idle')
const currentIndex = ref(0)
const correctCount = ref(0)
const score = ref(0)
const answered = ref(false)
const selectedOption = ref(null)
const startTime = ref(0)

// 数列推理题库
const questions = [
  { sequence: [2, 4, 6, 8], answer: 10, options: [9, 10, 11, 12] },
  { sequence: [1, 3, 9, 27], answer: 81, options: [54, 72, 81, 90] },
  { sequence: [1, 1, 2, 3, 5, 8], answer: 13, options: [11, 12, 13, 14] },
  { sequence: [100, 90, 80, 70], answer: 60, options: [55, 60, 65, 70] },
  { sequence: [2, 6, 12, 20, 30], answer: 42, options: [36, 40, 42, 44] },
  { sequence: [1, 4, 9, 16, 25], answer: 36, options: [30, 33, 36, 40] },
  { sequence: [3, 6, 11, 18, 27], answer: 38, options: [34, 36, 38, 40] },
  { sequence: [1, 2, 4, 7, 11, 16], answer: 22, options: [20, 21, 22, 23] },
]

const currentQuestion = computed(() => questions[currentIndex.value])

const startGame = () => {
  currentIndex.value = 0
  correctCount.value = 0
  score.value = 0
  answered.value = false
  selectedOption.value = null
  startTime.value = Date.now()
  gameState.value = 'playing'
}

const selectOption = (opt) => {
  if (answered.value) return
  selectedOption.value = opt
  answered.value = true
  if (opt === currentQuestion.value.answer) {
    correctCount.value++
    score.value += 12
  }
  // 延迟进入下一题
  setTimeout(() => {
    if (currentIndex.value < questions.length - 1) {
      currentIndex.value++
      answered.value = false
      selectedOption.value = null
    } else {
      finishGame()
    }
  }, 1000)
}

const finishGame = () => {
  const duration = Math.floor((Date.now() - startTime.value) / 1000)
  gameState.value = 'finished'
  submitScore(duration)
}

const submitScore = async (duration) => {
  if (!userStore.isLoggedIn) return
  try {
    await request.post('/training/submit', {
      game_type: 'logic',
      score: score.value,
      difficulty: 2,
      duration,
    })
  } catch (e) {
    console.log('提交失败', e)
  }
}

const resetGame = () => { gameState.value = 'idle' }
const goBack = () => { uni.switchTab({ url: '/pages/index/index' }) }
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 24rpx; }

.game-header {
  background: linear-gradient(135deg, #ffecd2, #fcb69f);
  border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .game-title { display: block; font-size: 40rpx; font-weight: bold; color: #333; margin-bottom: 10rpx; }
  .game-desc { display: block; font-size: 24rpx; color: #555; }
}

.quiz-section {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .quiz-progress { display: flex; justify-content: space-between; font-size: 26rpx; color: #888; margin-bottom: 30rpx; }
  .quiz-question { margin-bottom: 40rpx; }
  .question-label { display: block; font-size: 28rpx; color: #666; margin-bottom: 20rpx; }
  .sequence-row { display: flex; flex-wrap: wrap; gap: 16rpx; align-items: center; }
  .seq-num {
    width: 80rpx; height: 80rpx; background: #f0f4ff; border-radius: 12rpx;
    display: flex; align-items: center; justify-content: center;
    font-size: 34rpx; font-weight: bold; color: #4a90e2; text-align: center; line-height: 80rpx;
    &.unknown { background: #4a90e2; color: #fff; }
  }
  .options-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16rpx; }
  .option-btn {
    background: #f5f5f5; border-radius: 16rpx; padding: 28rpx; text-align: center;
    font-size: 38rpx; font-weight: bold; color: #333;
    &.correct { background: #52c41a; color: #fff; }
    &.wrong { background: #ff4d4f; color: #fff; }
  }
  .hint-text { display: block; text-align: center; font-size: 28rpx; margin-top: 20rpx; color: #555; }
}

.start-section {
  background: #fff; border-radius: 20rpx; padding: 40rpx; text-align: center;
  .start-desc { display: block; font-size: 28rpx; color: #666; margin-bottom: 30rpx; }
}

.start-btn {
  width: 100%; height: 90rpx;
  background: linear-gradient(90deg, #ffecd2, #fcb69f);
  color: #333; font-size: 34rpx; font-weight: bold; border-radius: 50rpx; border: none;
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
