<template>
  <view class="page-container">
    <view class="welcome-section">
      <text class="welcome-title">🧠 脑力锻炼</text>
      <text class="welcome-subtitle">每天训练，保持大脑活力</text>
      <text class="user-greeting" v-if="userStore.isLoggedIn">
        你好，{{ userStore.userInfo.nickname || userStore.userInfo.username }} 👋
      </text>
    </view>

    <view class="stats-card card">
      <text class="card-title">📊 今日训练</text>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">{{ todayStats.count }}</text>
          <text class="stat-label">训练次数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ Math.round(todayStats.duration / 60) }}</text>
          <text class="stat-label">训练分钟</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ todayStats.avgScore }}</text>
          <text class="stat-label">平均分</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ streakDays }}</text>
          <text class="stat-label">连续天数</text>
        </view>
      </view>
    </view>

    <view class="daily-tasks-card card" v-if="userStore.isLoggedIn && dailyTasks.length > 0">
      <text class="card-title">📋 今日任务</text>
      <view
        v-for="task in dailyTasks"
        :key="task.id"
        class="daily-task-item"
        :class="{ completed: task.is_completed }"
      >
        <text class="task-check">{{ task.is_completed ? '✅' : '⬜' }}</text>
        <text class="task-desc">{{ task.task_desc }}</text>
        <text class="task-progress">{{ task.current_value }}/{{ task.target_value }}</text>
      </view>
    </view>

    <view class="recommend-card card" v-if="recommendations.length > 0">
      <text class="card-title">💡 今日推荐</text>
      <view
        v-for="rec in recommendations"
        :key="rec.game_type"
        class="recommend-item"
        @click="goToGame(gamePathMap[rec.game_type])"
      >
        <text class="rec-icon">{{ gameIconMap[rec.game_type] }}</text>
        <view class="rec-info">
          <text class="rec-name">{{ rec.name }}</text>
          <text class="rec-reason">{{ rec.reason }}</text>
        </view>
        <text class="rec-arrow">›</text>
      </view>
    </view>

    <view class="section-title">🎮 训练模块</view>
    <view class="game-grid">
      <view
        v-for="game in games"
        :key="game.type"
        class="game-card"
        :style="{ backgroundColor: game.color }"
        @click="goToGame(game.path)"
      >
        <text class="game-icon">{{ game.icon }}</text>
        <text class="game-name">{{ game.name }}</text>
        <text class="game-desc">{{ game.desc }}</text>
        <text class="game-new" v-if="game.isNew">NEW</text>
      </view>
    </view>

    <view class="quick-actions">
      <button class="action-btn" @click="goToReport">📈 查看报告</button>
      <button class="action-btn" @click="goToProfile">👤 个人中心</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()

const todayStats = ref({ count: 0, duration: 0, avgScore: 0 })
const streakDays = ref(0)
const dailyTasks = ref([])
const recommendations = ref([])

const gameIconMap = {
  memory: '🃏', attention: '🎯', calculation: '🔢', logic: '🧩', language: '💬',
  spatial: '🧭', face: '👤', rhythm: '🎵', classification: '📂', dual_task: '🔄',
}

const gamePathMap = {
  memory: '/pages/train/memory/memory',
  attention: '/pages/train/attention/attention',
  calculation: '/pages/train/calculation/calculation',
  logic: '/pages/train/logic/logic',
  language: '/pages/train/language/language',
  spatial: '/pages/train/spatial/spatial',
  face: '/pages/train/face/face',
  rhythm: '/pages/train/rhythm/rhythm',
  classification: '/pages/train/classification/classification',
  dual_task: '/pages/train/dual_task/dual_task',
}

const games = [
  { type: 'memory', name: '记忆力', icon: '🃏', desc: '翻牌配对', color: '#ff9a9e', path: '/pages/train/memory/memory', isNew: false },
  { type: 'attention', name: '注意力', icon: '🎯', desc: '舒尔特方格', color: '#a1c4fd', path: '/pages/train/attention/attention', isNew: false },
  { type: 'calculation', name: '计算力', icon: '🔢', desc: '速算挑战', color: '#84fab0', path: '/pages/train/calculation/calculation', isNew: false },
  { type: 'logic', name: '逻辑推理', icon: '🧩', desc: '图形推理', color: '#ffecd2', path: '/pages/train/logic/logic', isNew: false },
  { type: 'language', name: '语言能力', icon: '💬', desc: '成语接龙', color: '#d4fc79', path: '/pages/train/language/language', isNew: false },
  { type: 'spatial', name: '空间定向', icon: '🧭', desc: '方向判断', color: '#667eea', path: '/pages/train/spatial/spatial', isNew: true },
  { type: 'face', name: '人脸识别', icon: '👤', desc: '面孔记忆', color: '#f093fb', path: '/pages/train/face/face', isNew: true },
  { type: 'rhythm', name: '节律训练', icon: '🎵', desc: '节拍复现', color: '#4facfe', path: '/pages/train/rhythm/rhythm', isNew: true },
  { type: 'classification', name: '分类归纳', icon: '📂', desc: '物品分类', color: '#43e97b', path: '/pages/train/classification/classification', isNew: true },
  { type: 'dual_task', name: '双重任务', icon: '🔄', desc: '一心二用', color: '#fa709a', path: '/pages/train/dual_task/dual_task', isNew: true },
]

const loadTodayStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/report/daily')
    todayStats.value = {
      count: res.total_count || 0,
      duration: res.total_duration || 0,
      avgScore: res.records?.length ? Math.round(res.records.reduce((s, r) => s + r.score, 0) / res.records.length) : 0,
    }
  } catch (e) {}
}

const loadStreakAndStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const stats = await request.get('/training/stats')
    streakDays.value = stats.streak_days || 0
  } catch (e) {}
}

const loadDailyTasks = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/daily-task/today')
    dailyTasks.value = res.tasks || []
  } catch (e) {}
}

const loadRecommendations = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/training/recommendations')
    recommendations.value = res.recommendations || []
  } catch (e) {}
}

const goToGame = (path) => {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/login' })
    return
  }
  uni.navigateTo({ url: path })
}

const goToReport = () => uni.switchTab({ url: '/pages/report/report' })
const goToProfile = () => uni.switchTab({ url: '/pages/profile/profile' })

onMounted(() => {
  loadTodayStats()
  loadStreakAndStats()
  loadDailyTasks()
  loadRecommendations()
})
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 30rpx; }

.welcome-section {
  background: linear-gradient(135deg, #4a90e2, #7ec8e3);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 30rpx;
  color: #fff;
  .welcome-title { display: block; font-size: 48rpx; font-weight: bold; margin-bottom: 10rpx; }
  .welcome-subtitle { display: block; font-size: 28rpx; opacity: 0.9; margin-bottom: 10rpx; }
  .user-greeting { display: block; font-size: 26rpx; opacity: 0.85; }
}

.stats-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
  .card-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .stats-row { display: flex; justify-content: space-around; }
  .stat-item { text-align: center; }
  .stat-value { display: block; font-size: 44rpx; font-weight: bold; color: #4a90e2; }
  .stat-label { display: block; font-size: 22rpx; color: #999; margin-top: 8rpx; }
}

.daily-tasks-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
  .card-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
  .daily-task-item {
    display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5;
    &.completed { opacity: 0.6; }
    &:last-child { border-bottom: none; }
    .task-check { margin-right: 16rpx; font-size: 28rpx; }
    .task-desc { flex: 1; font-size: 26rpx; color: #333; }
    .task-progress { font-size: 22rpx; color: #999; }
  }
}

.recommend-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.08);
  .card-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
  .recommend-item {
    display: flex; align-items: center; padding: 16rpx 0; border-bottom: 1rpx solid #f5f5f5;
    &:last-child { border-bottom: none; }
    &:active { background: #fafafa; }
    .rec-icon { font-size: 40rpx; margin-right: 16rpx; }
    .rec-info { flex: 1; }
    .rec-name { display: block; font-size: 28rpx; font-weight: bold; color: #333; }
    .rec-reason { display: block; font-size: 22rpx; color: #999; margin-top: 4rpx; }
    .rec-arrow { font-size: 36rpx; color: #ccc; }
  }
}

.section-title { font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }

.game-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.game-card {
  border-radius: 20rpx; padding: 30rpx 24rpx;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 4rpx 15rpx rgba(0,0,0,0.1);
  position: relative;
  &:active { opacity: 0.85; }
  .game-icon { font-size: 56rpx; margin-bottom: 12rpx; }
  .game-name { font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 8rpx; }
  .game-desc { font-size: 22rpx; color: #666; }
  .game-new {
    position: absolute; top: 10rpx; right: 10rpx;
    background: #ff4d4f; color: #fff; font-size: 18rpx;
    padding: 2rpx 10rpx; border-radius: 8rpx; font-weight: bold;
  }
}

.quick-actions {
  display: flex; gap: 20rpx;
  .action-btn {
    flex: 1; background: #fff; color: #4a90e2; border: 2rpx solid #4a90e2;
    border-radius: 50rpx; padding: 22rpx 0; font-size: 28rpx; text-align: center;
    &:active { background: #4a90e2; color: #fff; }
  }
}
</style>
