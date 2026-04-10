<template>
  <view class="page-container">
    <GameLayout
      title="👤 人脸识别"
      description="记住面孔，找出正确的人！"
      headerGradient="linear-gradient(135deg, #f093fb, #f5576c)"
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

      <view class="face-game">
        <view class="preview-phase" v-if="gameState === 'preview'">
          <text class="preview-tip">👀 记住这张脸！</text>
          <view class="face-card target-face">
            <text class="face-emoji">{{ targetFace }}</text>
            <text class="face-name">{{ targetName }}</text>
          </view>
          <text class="countdown">{{ previewCountdown }} 秒</text>
        </view>

        <view class="select-phase" v-if="gameState === 'playing' && !showingResult">
          <text class="select-tip">选出刚才看到的人</text>
          <view class="face-options" :class="{ 'grid-3': faceOptions.length > 4 }">
            <view
              v-for="(face, idx) in faceOptions"
              :key="idx"
              class="face-card option-face"
              :class="{ selected: selectedIdx === idx, correct: showingResult && idx === targetIdx }"
              @click="selectFace(idx)"
            >
              <text class="face-emoji">{{ face.emoji }}</text>
              <text class="face-name">{{ face.name }}</text>
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
      storageKey="guide_face"
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
const targetFace = ref('')
const targetName = ref('')
const targetIdx = ref(0)
const faceOptions = ref([])
const selectedIdx = ref(null)
const showingResult = ref(false)
const showFeedback = ref(false)
const feedbackType = ref('correct')
const showGuide = ref(false)
const previewCountdown = ref(3)

let timer = null
let previewTimer = null

const difficulties = [
  { level: 1, name: '简单', desc: '3选1' },
  { level: 2, name: '中等', desc: '4选1' },
  { level: 3, name: '困难', desc: '6选1' },
]

const guideSteps = [
  { icon: '👤', title: '人脸识别训练', desc: '锻炼你的面孔识别和记忆能力', animation: '👤' },
  { icon: '👀', title: '记住面孔', desc: '屏幕会显示一张面孔，仔细记住他/她的特征' },
  { icon: '🔍', title: '找出目标', desc: '从多张面孔中选出刚才看到的那个人' },
  { icon: '🧠', title: '难度递增', desc: '难度越高，选项越多，干扰越大！' },
]

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

const FACE_POOL = [
  { emoji: '👨', name: '张三' },
  { emoji: '👩', name: '李四' },
  { emoji: '👴', name: '王五' },
  { emoji: '👵', name: '赵六' },
  { emoji: '👦', name: '孙七' },
  { emoji: '👧', name: '周八' },
  { emoji: '🧑', name: '吴九' },
  { emoji: '👱', name: '郑十' },
  { emoji: '👲', name: '钱一' },
  { emoji: '🧔', name: '冯二' },
]

const formatTime = (s) => {
  return `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`
}

const startGame = () => {
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

  const optionCount = selectedDifficulty.value === 1 ? 3 : selectedDifficulty.value === 2 ? 4 : 6
  const shuffled = [...FACE_POOL].sort(() => Math.random() - 0.5)
  const target = shuffled[0]
  targetFace.value = target.emoji
  targetName.value = target.name

  const options = [target]
  for (let i = 1; i < optionCount && i < shuffled.length; i++) {
    options.push(shuffled[i])
  }
  options.sort(() => Math.random() - 0.5)
  targetIdx.value = options.findIndex(o => o.emoji === target.emoji)
  faceOptions.value = options
  selectedIdx.value = null
  showingResult.value = false

  gameState.value = 'preview'
  previewCountdown.value = selectedDifficulty.value === 3 ? 2 : 3

  clearInterval(previewTimer)
  previewTimer = setInterval(() => {
    previewCountdown.value--
    if (previewCountdown.value <= 0) {
      clearInterval(previewTimer)
      gameState.value = 'playing'
      if (!timer) {
        timer = setInterval(() => { timeElapsed.value++ }, 1000)
      }
    }
  }, 1000)
}

const selectFace = (idx) => {
  if (showingResult.value) return
  selectedIdx.value = idx
  showingResult.value = true
  currentRound.value++

  const isCorrect = idx === targetIdx.value
  if (isCorrect) {
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
  clearInterval(previewTimer)
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
      game_type: 'face',
      score: score.value,
      difficulty: selectedDifficulty.value,
      duration: timeElapsed.value,
      is_practice: isPractice.value ? 1 : 0,
    })
  } catch (e) { console.log('提交成绩失败', e) }
}

const resetGame = () => {
  clearInterval(timer)
  clearInterval(previewTimer)
  timer = null
  gameState.value = 'idle'
}

const loadRecommendation = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/training/recommend', { params: { game_type: 'face' } })
    recommendedDiff.value = res.recommended_difficulty
  } catch (e) {}
}

onMounted(() => {
  try { const g = uni.getStorageSync('guide_face'); if (!g) showGuide.value = true } catch(e) {}
  loadRecommendation()
})

onUnmounted(() => { clearInterval(timer); clearInterval(previewTimer) })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; }

.face-game { display: flex; flex-direction: column; align-items: center; }

.preview-phase {
  text-align: center;
  padding: 40rpx;

  .preview-tip { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 30rpx; }
  .countdown { display: block; font-size: 48rpx; font-weight: bold; color: #f5576c; margin-top: 20rpx; }
}

.face-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 15rpx rgba(0,0,0,0.1);

  &.target-face {
    width: 280rpx;
    margin: 0 auto;
    border: 3rpx solid #f093fb;
  }

  &.option-face {
    border: 3rpx solid #e8e8e8;
    &.selected { border-color: #f093fb; background: rgba(240, 147, 251, 0.1); }
    &.correct { border-color: #52c41a; background: rgba(82, 196, 26, 0.1); }
    &:active { transform: scale(0.95); }
  }

  .face-emoji { font-size: 80rpx; margin-bottom: 10rpx; }
  .face-name { font-size: 26rpx; color: #555; }
}

.select-phase {
  text-align: center;
  padding: 20rpx;

  .select-tip { display: block; font-size: 34rpx; font-weight: bold; color: #333; margin-bottom: 30rpx; }
}

.face-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  max-width: 500rpx;
  margin: 0 auto;

  &.grid-3 { grid-template-columns: repeat(3, 1fr); }
}

.result-stats {
  display: flex; flex-direction: column; gap: 10rpx;
  .result-stat { font-size: 28rpx; color: #666; }
}
</style>
