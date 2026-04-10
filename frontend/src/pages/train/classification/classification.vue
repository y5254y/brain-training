<template>
  <view class="page-container">
    <GameLayout
      title="📂 分类归纳"
      description="将物品归入正确的类别！"
      headerGradient="linear-gradient(135deg, #43e97b, #38f9d7)"
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

      <view class="classification-game">
        <view class="item-display" v-if="gameState === 'playing' && !showingResult">
          <text class="item-emoji">{{ currentItem.emoji }}</text>
          <text class="item-name">{{ currentItem.name }}</text>
          <text class="classify-tip">归类到：</text>
          <view class="category-options">
            <view
              v-for="cat in categories"
              :key="cat.name"
              class="category-btn"
              :class="{ selected: selectedCategory === cat.name }"
              :style="{ borderColor: cat.color }"
              @click="selectCategory(cat.name)"
            >
              <text class="cat-icon">{{ cat.icon }}</text>
              <text class="cat-name">{{ cat.name }}</text>
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
      storageKey="guide_classification"
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
const currentItem = ref({})
const categories = ref([])
const selectedCategory = ref(null)
const showingResult = ref(false)
const showFeedback = ref(false)
const feedbackType = ref('correct')
const showGuide = ref(false)
const items = ref([])

let timer = null

const difficulties = [
  { level: 1, name: '简单', desc: '3类' },
  { level: 2, name: '中等', desc: '4类' },
  { level: 3, name: '困难', desc: '5类' },
]

const guideSteps = [
  { icon: '📂', title: '分类归纳训练', desc: '锻炼你的语义记忆和归纳能力', animation: '📂' },
  { icon: '👀', title: '看物品', desc: '屏幕会显示一个物品' },
  { icon: '🤔', title: '选类别', desc: '从多个类别中选出该物品所属的正确类别' },
  { icon: '🧠', title: '越快越好', desc: '难度越高，类别越多，分类越细！' },
]

const CATEGORY_POOLS = [
  [
    { name: '水果', icon: '🍎', color: '#ff9a9e', items: [
      { emoji: '🍎', name: '苹果' }, { emoji: '🍌', name: '香蕉' }, { emoji: '🍇', name: '葡萄' },
      { emoji: '🍊', name: '橙子' }, { emoji: '🍓', name: '草莓' }, { emoji: '🍑', name: '桃子' },
    ]},
    { name: '动物', icon: '🐶', color: '#a1c4fd', items: [
      { emoji: '🐶', name: '小狗' }, { emoji: '🐱', name: '小猫' }, { emoji: '🐼', name: '熊猫' },
      { emoji: '🦊', name: '狐狸' }, { emoji: '🐸', name: '青蛙' }, { emoji: '🦁', name: '狮子' },
    ]},
    { name: '交通', icon: '🚗', color: '#84fab0', items: [
      { emoji: '🚗', name: '汽车' }, { emoji: '✈️', name: '飞机' }, { emoji: '🚢', name: '轮船' },
      { emoji: '🚂', name: '火车' }, { emoji: '🚲', name: '自行车' }, { emoji: '🚌', name: '公交车' },
    ]},
  ],
  [
    { name: '乐器', icon: '🎸', color: '#ffecd2', items: [
      { emoji: '🎸', name: '吉他' }, { emoji: '🎹', name: '钢琴' }, { emoji: '🥁', name: '鼓' },
      { emoji: '🎻', name: '小提琴' }, { emoji: '🎺', name: '小号' },
    ]},
    { name: '天气', icon: '🌤', color: '#d4fc79', items: [
      { emoji: '☀️', name: '晴天' }, { emoji: '🌧', name: '下雨' }, { emoji: '❄️', name: '下雪' },
      { emoji: '⛈', name: '雷暴' }, { emoji: '🌫', name: '大雾' },
    ]},
  ],
  [
    { name: '运动', icon: '⚽', color: '#667eea', items: [
      { emoji: '⚽', name: '足球' }, { emoji: '🏀', name: '篮球' }, { emoji: '🏊', name: '游泳' },
      { emoji: '🎾', name: '网球' }, { emoji: '🤸', name: '体操' },
    ]},
    { name: '职业', icon: '👨‍⚕️', color: '#f093fb', items: [
      { emoji: '👨‍⚕️', name: '医生' }, { emoji: '👨‍🏫', name: '老师' }, { emoji: '👨‍🍳', name: '厨师' },
      { emoji: '👮', name: '警察' }, { emoji: '👨‍🔧', name: '修理工' },
    ]},
  ],
]

const totalRounds = computed(() => 10)
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

const startGame = () => {
  const catCount = selectedDifficulty.value === 1 ? 3 : selectedDifficulty.value === 2 ? 4 : 5
  const allCats = [...CATEGORY_POOLS[0]]
  if (catCount >= 4) allCats.push(...CATEGORY_POOLS[1])
  if (catCount >= 5) allCats.push(...CATEGORY_POOLS[2])
  categories.value = allCats.slice(0, catCount)

  const allItems = []
  categories.value.forEach(cat => {
    cat.items.forEach(item => {
      allItems.push({ ...item, category: cat.name })
    })
  })
  items.value = allItems.sort(() => Math.random() - 0.5).slice(0, totalRounds.value)

  currentRound.value = 0
  correctCount.value = 0
  timeElapsed.value = 0
  score.value = 0
  timer = setInterval(() => { timeElapsed.value++ }, 1000)
  nextRound()
}

const nextRound = () => {
  if (currentRound.value >= items.value.length) {
    finishGame()
    return
  }
  currentItem.value = items.value[currentRound.value]
  selectedCategory.value = null
  showingResult.value = false
  gameState.value = 'playing'
}

const selectCategory = (catName) => {
  if (showingResult.value) return
  selectedCategory.value = catName
  showingResult.value = true
  currentRound.value++

  const isCorrect = catName === currentItem.value.category
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
      game_type: 'classification',
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
    const res = await request.get('/training/recommend', { params: { game_type: 'classification' } })
    recommendedDiff.value = res.recommended_difficulty
  } catch (e) {}
}

onMounted(() => {
  try { const g = uni.getStorageSync('guide_classification'); if (!g) showGuide.value = true } catch(e) {}
  loadRecommendation()
})

onUnmounted(() => { clearInterval(timer) })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; }

.classification-game { display: flex; flex-direction: column; align-items: center; padding: 20rpx; }

.item-display {
  text-align: center;
  padding: 20rpx;

  .item-emoji { display: block; font-size: 100rpx; margin-bottom: 16rpx; }
  .item-name { display: block; font-size: 36rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
  .classify-tip { display: block; font-size: 28rpx; color: #666; margin-bottom: 24rpx; }
}

.category-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  max-width: 500rpx;
  margin: 0 auto;
}

.category-btn {
  background: #fff;
  border: 3rpx solid #e8e8e8;
  border-radius: 20rpx;
  padding: 24rpx 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;

  &.selected {
    background: rgba(67, 233, 123, 0.1);
    border-width: 3rpx;
  }

  &:active { transform: scale(0.95); }

  .cat-icon { font-size: 48rpx; }
  .cat-name { font-size: 26rpx; color: #555; font-weight: bold; }
}

.result-stats {
  display: flex; flex-direction: column; gap: 10rpx;
  .result-stat { font-size: 28rpx; color: #666; }
}
</style>
