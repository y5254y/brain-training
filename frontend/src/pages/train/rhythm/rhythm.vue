<template>
  <view class="page-container">
    <GameLayout
      title="🎵 节律训练"
      description="跟随节拍，复现节奏！"
      headerGradient="linear-gradient(135deg, #4facfe, #00f2fe)"
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

      <view class="rhythm-game">
        <view class="listen-phase" v-if="phase === 'listen'">
          <text class="phase-tip">👂 听节奏</text>
          <view class="beat-display">
            <view
              v-for="(beat, idx) in currentPattern"
              :key="idx"
              class="beat-dot"
              :class="{ active: playingIdx === idx, rest: beat === 0 }"
            >
              <text v-if="beat === 1">🎵</text>
              <text v-else>·</text>
            </view>
          </view>
        </view>

        <view class="repeat-phase" v-if="phase === 'repeat'">
          <text class="phase-tip">👆 复现节奏</text>
          <view class="beat-display">
            <view
              v-for="(beat, idx) in currentPattern"
              :key="idx"
              class="beat-dot"
              :class="{ active: userPlayingIdx === idx, rest: beat === 0, hit: userPattern[idx] === 1, miss: userPattern[idx] === -1 }"
            >
              <text v-if="userPattern[idx] === 1">🎵</text>
              <text v-else-if="userPattern[idx] === -1">✗</text>
              <text v-else>·</text>
            </view>
          </view>
          <view class="tap-area">
            <view
              class="tap-btn"
              :class="{ pressed: isTapping }"
              @touchstart="onTapStart"
              @touchend="onTapEnd"
            >
              <text class="tap-icon">🥁</text>
              <text class="tap-text">敲击</text>
            </view>
            <view class="skip-btn" @click="skipBeat">
              <text>跳过（休止符）</text>
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
      storageKey="guide_rhythm"
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
const phase = ref('')
const currentPattern = ref([])
const userPattern = ref([])
const playingIdx = ref(-1)
const userPlayingIdx = ref(-1)
const isTapping = ref(false)
const showFeedback = ref(false)
const feedbackType = ref('correct')
const showGuide = ref(false)

let timer = null
let playTimer = null
let beatTimer = null

const difficulties = [
  { level: 1, name: '简单', desc: '4拍' },
  { level: 2, name: '中等', desc: '6拍' },
  { level: 3, name: '困难', desc: '8拍' },
]

const guideSteps = [
  { icon: '🎵', title: '节律训练', desc: '锻炼你的节奏感知和时间记忆能力', animation: '🎵' },
  { icon: '👂', title: '听节奏', desc: '仔细听屏幕上播放的节奏模式' },
  { icon: '👆', title: '复现节奏', desc: '按照听到的节奏，敲击按钮复现' },
  { icon: '⏭', title: '跳过休止', desc: '遇到休止符（·）时，点击"跳过"按钮' },
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

const formatTime = (s) => `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`

const generatePattern = () => {
  const len = selectedDifficulty.value === 1 ? 4 : selectedDifficulty.value === 2 ? 6 : 8
  const pattern = []
  for (let i = 0; i < len; i++) {
    pattern.push(Math.random() > 0.3 ? 1 : 0)
  }
  if (pattern.every(p => p === 0)) pattern[0] = 1
  return pattern
}

const startGame = () => {
  currentRound.value = 0
  correctCount.value = 0
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

  currentPattern.value = generatePattern()
  userPattern.value = new Array(currentPattern.value.length).fill(0)
  playingIdx.value = -1
  userPlayingIdx.value = -1
  phase.value = 'listen'
  gameState.value = 'playing'

  playPattern()
}

const playPattern = () => {
  let idx = 0
  const interval = 600
  playTimer = setInterval(() => {
    if (idx < currentPattern.value.length) {
      playingIdx.value = idx
      if (currentPattern.value[idx] === 1) {
        try { uni.vibrateShort({ type: 'light' }) } catch(e) {}
      }
      idx++
    } else {
      clearInterval(playTimer)
      playingIdx.value = -1
      phase.value = 'repeat'
      userPlayingIdx.value = 0
    }
  }, interval)
}

const onTapStart = () => {
  isTapping.value = true
  if (phase.value !== 'repeat') return
  if (userPlayingIdx.value >= currentPattern.value.length) return

  const idx = userPlayingIdx.value
  if (currentPattern.value[idx] === 1) {
    userPattern.value[idx] = 1
  } else {
    userPattern.value[idx] = -1
  }
  try { uni.vibrateShort({ type: 'light' }) } catch(e) {}
  advanceBeat()
}

const onTapEnd = () => { isTapping.value = false }

const skipBeat = () => {
  if (phase.value !== 'repeat') return
  if (userPlayingIdx.value >= currentPattern.value.length) return

  const idx = userPlayingIdx.value
  if (currentPattern.value[idx] === 0) {
    userPattern.value[idx] = 0
  } else {
    userPattern.value[idx] = -1
  }
  advanceBeat()
}

const advanceBeat = () => {
  userPlayingIdx.value++
  if (userPlayingIdx.value >= currentPattern.value.length) {
    checkRound()
  }
}

const checkRound = () => {
  currentRound.value++
  const isCorrect = userPattern.value.every((v, i) => {
    if (currentPattern.value[i] === 1) return v === 1
    return v === 0
  })

  if (isCorrect) {
    correctCount.value++
    feedbackType.value = 'correct'
  } else {
    feedbackType.value = 'wrong'
  }

  showFeedback.value = true
  setTimeout(() => { showFeedback.value = false }, 600)

  setTimeout(() => { nextRound() }, 1000)
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
      game_type: 'rhythm',
      score: score.value,
      difficulty: selectedDifficulty.value,
      duration: timeElapsed.value,
      is_practice: isPractice.value ? 1 : 0,
    })
  } catch (e) {}
}

const resetGame = () => {
  clearInterval(timer)
  clearInterval(playTimer)
  timer = null
  gameState.value = 'idle'
  phase.value = ''
}

const loadRecommendation = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/training/recommend', { params: { game_type: 'rhythm' } })
    recommendedDiff.value = res.recommended_difficulty
  } catch (e) {}
}

onMounted(() => {
  try { const g = uni.getStorageSync('guide_rhythm'); if (!g) showGuide.value = true } catch(e) {}
  loadRecommendation()
})

onUnmounted(() => { clearInterval(timer); clearInterval(playTimer) })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; }

.rhythm-game { display: flex; flex-direction: column; align-items: center; padding: 20rpx; }

.phase-tip {
  display: block;
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 30rpx;
}

.beat-display {
  display: flex;
  gap: 16rpx;
  justify-content: center;
  margin-bottom: 40rpx;
  flex-wrap: wrap;
}

.beat-dot {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  transition: all 0.2s;

  &.active {
    background: #4facfe;
    transform: scale(1.2);
    color: #fff;
  }

  &.hit {
    background: #52c41a;
    color: #fff;
  }

  &.miss {
    background: #ff4d4f;
    color: #fff;
  }

  &.rest {
    background: #e8e8e8;
  }
}

.tap-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

.tap-btn {
  width: 240rpx;
  height: 240rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 30rpx rgba(79, 172, 254, 0.4);

  &.pressed {
    transform: scale(0.9);
    box-shadow: 0 4rpx 15rpx rgba(79, 172, 254, 0.3);
  }

  .tap-icon { font-size: 80rpx; }
  .tap-text { font-size: 28rpx; color: #fff; font-weight: bold; margin-top: 8rpx; }
}

.skip-btn {
  padding: 16rpx 40rpx;
  background: #f0f0f0;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
}

.result-stats {
  display: flex; flex-direction: column; gap: 10rpx;
  .result-stat { font-size: 28rpx; color: #666; }
}
</style>
