<template>
  <view class="page-container">
    <view class="page-header">
      <text class="page-title">📈 训练报告</text>
    </view>

    <view class="login-tip card" v-if="!userStore.isLoggedIn">
      <text class="tip-text">请先登录以查看训练报告</text>
      <button class="go-login-btn" @click="goLogin">去登录</button>
    </view>

    <template v-else>
      <view class="period-tabs">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activePeriod === tab.key }"
          @click="activePeriod = tab.key; loadReport()"
        >{{ tab.label }}</view>
      </view>

      <view class="summary-card card">
        <text class="card-title">总体情况</text>
        <view class="summary-stats">
          <view class="stat-item">
            <text class="stat-value">{{ reportData.totalCount || 0 }}</text>
            <text class="stat-label">总训练次数</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ Math.round((reportData.totalDuration || 0) / 60) }}</text>
            <text class="stat-label">总训练分钟</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ activeDays }}</text>
            <text class="stat-label">活跃天数</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ streakDays }}</text>
            <text class="stat-label">连续天数</text>
          </view>
        </view>
      </view>

      <view class="radar-card card">
        <text class="card-title">🕸 认知能力雷达图</text>
        <view class="radar-chart">
          <view class="radar-svg">
            <view
              v-for="(ability, idx) in abilities"
              :key="ability.key"
              class="radar-axis"
              :style="{ transform: `rotate(${idx * 36}deg)` }"
            >
              <view class="axis-line"></view>
            </view>
            <view
              v-for="(ability, idx) in abilities"
              :key="'label-'+ability.key"
              class="radar-label"
              :style="getLabelPosition(idx)"
            >
              <text class="label-icon">{{ ability.icon }}</text>
              <text class="label-score">{{ radarData[ability.key] || 0 }}</text>
            </view>
          </view>
        </view>
        <view class="ability-list">
          <view v-for="ability in abilities" :key="ability.key" class="ability-item">
            <text class="ability-name">{{ ability.icon }} {{ ability.name }}</text>
            <view class="ability-bar-wrap">
              <view class="ability-bar" :style="{ width: `${radarData[ability.key] || 0}%`, backgroundColor: ability.color }"></view>
            </view>
            <text class="ability-score">{{ radarData[ability.key] || 0 }}</text>
          </view>
        </view>
      </view>

      <view class="comparison-card card" v-if="comparison.percentiles">
        <text class="card-title">👥 同龄对比</text>
        <view v-for="ability in abilities" :key="'comp-'+ability.key" class="comp-item">
          <text class="comp-name">{{ ability.icon }} {{ ability.name }}</text>
          <text class="comp-percentile">超过 {{ comparison.percentiles?.[ability.key] || 0 }}% 同龄人</text>
          <view class="comp-bar-wrap">
            <view class="comp-bar" :style="{ width: `${comparison.percentiles?.[ability.key] || 0}%` }"></view>
          </view>
        </view>
      </view>

      <view class="trend-card card" v-if="trendData.length > 0">
        <text class="card-title">📊 近7天趋势</text>
        <view class="trend-chart">
          <view v-for="item in trendData" :key="item.date" class="trend-bar-item">
            <view class="trend-bar-wrap">
              <view class="trend-bar" :style="{ height: `${item.avg_score}%` }"></view>
            </view>
            <text class="trend-date">{{ item.date.slice(5) }}</text>
          </view>
        </view>
      </view>

      <view class="records-card card">
        <text class="card-title">最近训练记录</text>
        <view v-if="recentRecords.length === 0" class="empty-tip">
          <text>暂无训练记录，快去训练吧！</text>
        </view>
        <view v-for="record in recentRecords" :key="record.id" class="record-item">
          <view class="record-left">
            <text class="record-type">{{ gameTypeMap[record.game_type] || record.game_type }}</text>
            <text class="record-time">{{ formatDate(record.created_at) }}</text>
          </view>
          <view class="record-right">
            <text class="record-score">{{ record.score }} 分</text>
            <text class="record-duration">{{ record.duration }}秒</text>
          </view>
        </view>
      </view>
    </template>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()

const activePeriod = ref('weekly')
const reportData = ref({})
const radarData = ref({})
const recentRecords = ref([])
const activeDays = ref(0)
const streakDays = ref(0)
const comparison = ref({})
const trendData = ref([])

const tabs = [
  { key: 'daily', label: '今日' },
  { key: 'weekly', label: '本周' },
  { key: 'monthly', label: '本月' },
]

const abilities = [
  { key: 'memory', name: '记忆力', icon: '🃏', color: '#ff9a9e' },
  { key: 'attention', name: '注意力', icon: '🎯', color: '#a1c4fd' },
  { key: 'calculation', name: '计算力', icon: '🔢', color: '#84fab0' },
  { key: 'logic', name: '逻辑推理', icon: '🧩', color: '#ffecd2' },
  { key: 'language', name: '语言能力', icon: '💬', color: '#d4fc79' },
  { key: 'spatial', name: '空间定向', icon: '🧭', color: '#667eea' },
  { key: 'face', name: '人脸识别', icon: '👤', color: '#f093fb' },
  { key: 'rhythm', name: '节律训练', icon: '🎵', color: '#4facfe' },
  { key: 'classification', name: '分类归纳', icon: '📂', color: '#43e97b' },
  { key: 'dual_task', name: '双重任务', icon: '🔄', color: '#fa709a' },
]

const gameTypeMap = {
  memory: '🃏 记忆力', attention: '🎯 注意力', calculation: '🔢 计算力',
  logic: '🧩 逻辑推理', language: '💬 语言能力', spatial: '🧭 空间定向',
  face: '👤 人脸识别', rhythm: '🎵 节律训练', classification: '📂 分类归纳',
  dual_task: '🔄 双重任务',
}

const getLabelPosition = (idx) => {
  const angle = (idx * 36 - 90) * Math.PI / 180
  const r = 42
  const x = 50 + r * Math.cos(angle)
  const y = 50 + r * Math.sin(angle)
  return { left: `${x}%`, top: `${y}%`, transform: 'translate(-50%, -50%)' }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth()+1}/${d.getDate()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`
}

const loadReport = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const report = await request.get(`/report/${activePeriod.value}`)
    reportData.value = { totalCount: report.total_count || 0, totalDuration: report.total_duration || 0 }
    activeDays.value = Object.keys(report.daily_data || {}).length || 0

    const radar = await request.get('/report/radar')
    radarData.value = radar.radar_data || {}

    const records = await request.get('/training/list', { params: { page: 1, page_size: 10 } })
    recentRecords.value = Array.isArray(records) ? records : []

    const stats = await request.get('/training/stats')
    streakDays.value = stats.streak_days || 0

    try {
      const comp = await request.get('/report/comparison')
      comparison.value = comp
    } catch (e) { comparison.value = {} }

    try {
      const trend = await request.get('/report/trend')
      trendData.value = trend.trend_data || []
    } catch (e) { trendData.value = [] }
  } catch (e) {
    console.log('加载报告失败', e)
  }
}

const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })

onMounted(() => { loadReport() })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 24rpx; }
.page-header { margin-bottom: 24rpx; .page-title { font-size: 44rpx; font-weight: bold; color: #333; } }

.login-tip {
  background: #fff; border-radius: 20rpx; padding: 60rpx; text-align: center;
  .tip-text { display: block; font-size: 28rpx; color: #999; margin-bottom: 30rpx; }
  .go-login-btn { background: #4a90e2; color: #fff; border-radius: 50rpx; padding: 20rpx 60rpx; font-size: 28rpx; border: none; }
}

.period-tabs {
  display: flex; background: #fff; border-radius: 50rpx; padding: 8rpx; margin-bottom: 24rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.06);
  .tab-item {
    flex: 1; text-align: center; padding: 18rpx 0; font-size: 28rpx; color: #888; border-radius: 50rpx;
    &.active { background: #4a90e2; color: #fff; font-weight: bold; }
  }
}

.summary-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .card-title { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .summary-stats { display: flex; justify-content: space-around; flex-wrap: wrap; }
  .stat-item { text-align: center; width: 25%; }
  .stat-value { display: block; font-size: 44rpx; font-weight: bold; color: #4a90e2; }
  .stat-label { display: block; font-size: 22rpx; color: #999; margin-top: 8rpx; }
}

.radar-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .card-title { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .radar-chart {
    position: relative; width: 100%; padding-top: 100%; margin-bottom: 30rpx;
  }
  .radar-svg {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
  }
  .radar-axis {
    position: absolute; width: 2rpx; height: 40%; background: #f0f0f0;
    transform-origin: bottom center; bottom: 50%;
  }
  .radar-label {
    position: absolute; text-align: center;
    .label-icon { display: block; font-size: 28rpx; }
    .label-score { display: block; font-size: 20rpx; color: #4a90e2; font-weight: bold; }
  }
  .ability-item {
    display: flex; align-items: center; margin-bottom: 16rpx;
    .ability-name { width: 160rpx; font-size: 24rpx; color: #555; }
    .ability-bar-wrap { flex: 1; height: 16rpx; background: #f0f0f0; border-radius: 8rpx; overflow: hidden; margin: 0 12rpx; }
    .ability-bar { height: 100%; border-radius: 8rpx; transition: width 0.5s ease; }
    .ability-score { width: 50rpx; text-align: right; font-size: 24rpx; font-weight: bold; color: #333; }
  }
}

.comparison-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .card-title { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .comp-item { margin-bottom: 16rpx; }
  .comp-name { font-size: 24rpx; color: #555; margin-right: 12rpx; }
  .comp-percentile { font-size: 22rpx; color: #4a90e2; font-weight: bold; }
  .comp-bar-wrap { height: 12rpx; background: #f0f0f0; border-radius: 6rpx; overflow: hidden; margin-top: 8rpx; }
  .comp-bar { height: 100%; background: linear-gradient(90deg, #4a90e2, #7ec8e3); border-radius: 6rpx; transition: width 0.5s ease; }
}

.trend-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .card-title { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .trend-chart { display: flex; align-items: flex-end; height: 200rpx; gap: 12rpx; }
  .trend-bar-item { flex: 1; display: flex; flex-direction: column; align-items: center; }
  .trend-bar-wrap { width: 100%; height: 160rpx; display: flex; align-items: flex-end; justify-content: center; }
  .trend-bar { width: 60%; background: linear-gradient(180deg, #4a90e2, #7ec8e3); border-radius: 8rpx 8rpx 0 0; min-height: 4rpx; transition: height 0.5s ease; }
  .trend-date { font-size: 20rpx; color: #999; margin-top: 8rpx; }
}

.records-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx;
  .card-title { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
  .empty-tip { text-align: center; padding: 40rpx; color: #ccc; font-size: 28rpx; }
  .record-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 20rpx 0; border-bottom: 1rpx solid #f0f0f0;
    &:last-child { border-bottom: none; }
    .record-left { display: flex; flex-direction: column; gap: 8rpx; }
    .record-type { font-size: 28rpx; color: #333; }
    .record-time { font-size: 22rpx; color: #999; }
    .record-right { text-align: right; }
    .record-score { display: block; font-size: 32rpx; font-weight: bold; color: #4a90e2; }
    .record-duration { display: block; font-size: 22rpx; color: #999; }
  }
}
</style>
