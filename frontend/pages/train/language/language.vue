<template>
  <view class="page-container">
    <view class="game-header card">
      <text class="game-title">💬 语言能力</text>
      <text class="game-desc">成语接龙 —— 根据提示词首字，完成成语接龙！</text>
    </view>

    <!-- 开始界面 -->
    <view class="start-section card" v-if="gameState === 'idle'">
      <text class="start-desc">
        游戏将给出一个字，你需要在10秒内输入以该字开头的四字成语。
        共 {{ totalRounds }} 轮，答对得10分！
      </text>
      <button class="start-btn" @click="startGame">开始游戏</button>
    </view>

    <!-- 游戏区域 -->
    <view class="game-area card" v-if="gameState === 'playing'">
      <view class="game-info">
        <text>第 {{ currentRound }}/{{ totalRounds }} 轮</text>
        <text class="timer" :class="{ urgent: timeLeft <= 3 }">⏱ {{ timeLeft }}s</text>
        <text>得分：{{ score }}</text>
      </view>

      <!-- 倒计时进度条 -->
      <view class="progress-bar">
        <view
          class="progress-fill"
          :style="{ width: `${(timeLeft / 10) * 100}%`, backgroundColor: timeLeft <= 3 ? '#ff4d4f' : '#4a90e2' }"
        ></view>
      </view>

      <!-- 提示词 -->
      <view class="hint-area">
        <text class="hint-label">请输入以「</text>
        <text class="hint-word">{{ currentHintChar }}</text>
        <text class="hint-label">」开头的四字成语：</text>
      </view>

      <!-- 输入区域 -->
      <view class="input-area">
        <input
          v-model="userInput"
          class="chengyu-input"
          placeholder="输入四字成语..."
          placeholder-class="input-placeholder"
          maxlength="4"
          @confirm="submitAnswer"
        />
        <button class="submit-btn" @click="submitAnswer">提交</button>
      </view>

      <!-- 反馈 -->
      <view class="feedback" v-if="feedback">
        <text :class="feedback.correct ? 'feedback-correct' : 'feedback-wrong'">
          {{ feedback.text }}
        </text>
      </view>

      <!-- 参考答案 -->
      <view class="examples" v-if="showExamples">
        <text class="examples-label">参考答案：</text>
        <text
          v-for="(ex, i) in currentExamples"
          :key="i"
          class="example-item"
        >{{ ex }}</text>
      </view>
    </view>

    <!-- 结果 -->
    <view class="result-section card" v-if="gameState === 'finished'">
      <text class="result-title">🎉 游戏结束！</text>
      <text class="result-score">得分：{{ score }}</text>
      <text class="result-correct">答对：{{ correctCount }}/{{ totalRounds }} 轮</text>
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

const gameState = ref('idle')
const currentRound = ref(0)
const totalRounds = 5
const score = ref(0)
const correctCount = ref(0)
const currentHintChar = ref('')
const userInput = ref('')
const feedback = ref(null)
const showExamples = ref(false)
const timeLeft = ref(10)
const startTime = ref(0)
let timer = null

// 成语题库（首字 → 参考成语列表）
const chengyuBank = [
  { char: '马', examples: ['马到成功', '马不停蹄', '马到功成', '马首是瞻'] },
  { char: '一', examples: ['一帆风顺', '一石二鸟', '一鸣惊人', '一往无前'] },
  { char: '心', examples: ['心旷神怡', '心花怒放', '心想事成', '心平气和'] },
  { char: '大', examples: ['大显身手', '大公无私', '大器晚成', '大智若愚'] },
  { char: '春', examples: ['春暖花开', '春风得意', '春回大地', '春意盎然'] },
  { char: '万', examples: ['万紫千红', '万象更新', '万无一失', '万古长青'] },
  { char: '百', examples: ['百年好合', '百折不挠', '百战百胜', '百花齐放'] },
  { char: '金', examples: ['金玉良言', '金碧辉煌', '金榜题名', '金声玉振'] },
]

const currentExamples = ref([])
let usedIndices = []

const getNextQuestion = () => {
  if (usedIndices.length === chengyuBank.length) usedIndices = []
  let idx
  do { idx = Math.floor(Math.random() * chengyuBank.length) } while (usedIndices.includes(idx))
  usedIndices.push(idx)
  return chengyuBank[idx]
}

const startGame = () => {
  currentRound.value = 0
  score.value = 0
  correctCount.value = 0
  usedIndices = []
  startTime.value = Date.now()
  gameState.value = 'playing'
  nextRound()
}

const nextRound = () => {
  if (currentRound.value >= totalRounds) {
    finishGame()
    return
  }
  currentRound.value++
  const q = getNextQuestion()
  currentHintChar.value = q.char
  currentExamples.value = q.examples
  userInput.value = ''
  feedback.value = null
  showExamples.value = false
  timeLeft.value = 10
  clearInterval(timer)
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      showExamples.value = true
      feedback.value = { correct: false, text: `超时！参考答案：${currentExamples.value[0]}` }
      setTimeout(nextRound, 2000)
    }
  }, 1000)
}

const submitAnswer = () => {
  if (!userInput.value.trim()) return
  clearInterval(timer)
  const input = userInput.value.trim()
  // 简单校验：首字匹配且为4个字
  const isCorrect =
    input.length === 4 && input[0] === currentHintChar.value
  if (isCorrect) {
    feedback.value = { correct: true, text: `✅ 答对了！+10分` }
    correctCount.value++
    score.value += 10
  } else {
    feedback.value = { correct: false, text: `❌ 不正确，需要以「${currentHintChar.value}」开头的四字成语` }
    showExamples.value = true
  }
  setTimeout(nextRound, 1500)
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
      game_type: 'language',
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

onUnmounted(() => { clearInterval(timer) })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 24rpx; }

.game-header {
  background: linear-gradient(135deg, #d4fc79, #96e6a1);
  border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .game-title { display: block; font-size: 40rpx; font-weight: bold; color: #333; margin-bottom: 10rpx; }
  .game-desc { display: block; font-size: 24rpx; color: #555; }
}

.start-section {
  background: #fff; border-radius: 20rpx; padding: 40rpx; text-align: center;
  .start-desc { display: block; font-size: 28rpx; color: #666; margin-bottom: 30rpx; line-height: 1.8; }
}

.start-btn {
  width: 100%; height: 90rpx;
  background: linear-gradient(90deg, #d4fc79, #96e6a1);
  color: #333; font-size: 34rpx; font-weight: bold; border-radius: 50rpx; border: none;
}

.game-area {
  background: #fff; border-radius: 20rpx; padding: 30rpx;
  .game-info {
    display: flex; justify-content: space-between; font-size: 26rpx; color: #555; margin-bottom: 16rpx;
    .timer { font-weight: bold; &.urgent { color: #ff4d4f; } }
  }
  .progress-bar { height: 12rpx; background: #f0f0f0; border-radius: 6rpx; margin-bottom: 40rpx; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 6rpx; transition: width 1s linear; }
  .hint-area { display: flex; align-items: center; flex-wrap: wrap; margin-bottom: 30rpx; }
  .hint-label { font-size: 30rpx; color: #555; }
  .hint-word { font-size: 56rpx; font-weight: bold; color: #4a90e2; margin: 0 8rpx; }
  .input-area { display: flex; gap: 16rpx; margin-bottom: 20rpx; }
  .chengyu-input {
    flex: 1; height: 88rpx; border: 2rpx solid #e8e8e8; border-radius: 12rpx;
    padding: 0 24rpx; font-size: 32rpx; color: #333; background: #fafafa;
  }
  .submit-btn {
    height: 88rpx; padding: 0 30rpx; background: #4a90e2; color: #fff;
    border-radius: 12rpx; font-size: 28rpx; border: none; white-space: nowrap;
  }
  .feedback { margin-bottom: 16rpx; }
  .feedback-correct { color: #52c41a; font-size: 28rpx; }
  .feedback-wrong { color: #ff4d4f; font-size: 28rpx; }
  .examples { background: #f9f9f9; border-radius: 12rpx; padding: 20rpx; }
  .examples-label { display: block; font-size: 26rpx; color: #888; margin-bottom: 12rpx; }
  .example-item { display: inline-block; margin: 6rpx 10rpx; font-size: 28rpx; color: #4a90e2; }
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
