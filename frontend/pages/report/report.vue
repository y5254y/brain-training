<template>
  <view class="page-container">
    <view class="page-header">
      <text class="page-title">📈 训练报告</text>
    </view>

    <!-- 未登录提示 -->
    <view class="login-tip card" v-if="!userStore.isLoggedIn">
      <text class="tip-text">请先登录以查看训练报告</text>
      <button class="go-login-btn" @click="goLogin">去登录</button>
    </view>

    <template v-else>
      <!-- 报告周期切换 -->
      <view class="period-tabs">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activePeriod === tab.key }"
          @click="activePeriod = tab.key; loadReport()"
        >
          {{ tab.label }}
        </view>
      </view>

      <!-- 综合统计 -->
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
        </view>
      </view>

      <!-- 各能力评分 -->
      <view class="radar-card card">
        <text class="card-title">🕸 认知能力分布</text>
        <view class="ability-list">
          <view
            v-for="ability in abilities"
            :key="ability.key"
            class="ability-item"
          >
            <text class="ability-name">{{ ability.icon }} {{ ability.name }}</text>
            <view class="ability-bar-wrap">
              <view
                class="ability-bar"
                :style="{
                  width: `${radarData[ability.key] || 0}%`,
                  backgroundColor: ability.color,
                }"
              ></view>
            </view>
            <text class="ability-score">{{ radarData[ability.key] || 0 }}</text>
          </view>
        </view>
      </view>

      <!-- 训练记录列表 -->
      <view class="records-card card">
        <text class="card-title">最近训练记录</text>
        <view v-if="recentRecords.length === 0" class="empty-tip">
          <text>暂无训练记录，快去训练吧！</text>
        </view>
        <view
          v-for="record in recentRecords"
          :key="record.id"
          class="record-item"
        >
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
]

const gameTypeMap = {
  memory: '🃏 记忆力',
  attention: '🎯 注意力',
  calculation: '🔢 计算力',
  logic: '🧩 逻辑推理',
  language: '💬 语言能力',
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const loadReport = async () => {
  if (!userStore.isLoggedIn) return
  try {
    // 加载报告数据
    const report = await request.get(`/report/${activePeriod.value}`)
    reportData.value = {
      totalCount: report.total_count || 0,
      totalDuration: report.total_duration || 0,
    }
    activeDays.value = Object.keys(report.daily_data || {}).length || 0

    // 加载雷达图数据
    const radar = await request.get('/report/radar')
    radarData.value = radar.radar_data || {}

    // 加载最近训练记录
    const records = await request.get('/training/list', { params: { page: 1, page_size: 10 } })
    recentRecords.value = Array.isArray(records) ? records : []
  } catch (e) {
    console.log('加载报告失败', e)
  }
}

const goLogin = () => {
  uni.navigateTo({ url: '/pages/login/login' })
}

onMounted(() => {
  loadReport()
})
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 24rpx;
}

.page-header {
  margin-bottom: 24rpx;
  .page-title { font-size: 44rpx; font-weight: bold; color: #333; }
}

.login-tip {
  background: #fff; border-radius: 20rpx; padding: 60rpx; text-align: center;
  .tip-text { display: block; font-size: 28rpx; color: #999; margin-bottom: 30rpx; }
  .go-login-btn {
    background: #4a90e2; color: #fff; border-radius: 50rpx;
    padding: 20rpx 60rpx; font-size: 28rpx; border: none;
  }
}

.period-tabs {
  display: flex; background: #fff; border-radius: 50rpx;
  padding: 8rpx; margin-bottom: 24rpx; box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.06);
  .tab-item {
    flex: 1; text-align: center; padding: 18rpx 0; font-size: 28rpx;
    color: #888; border-radius: 50rpx;
    &.active { background: #4a90e2; color: #fff; font-weight: bold; }
  }
}

.summary-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .card-title { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .summary-stats { display: flex; justify-content: space-around; }
  .stat-item { text-align: center; }
  .stat-value { display: block; font-size: 48rpx; font-weight: bold; color: #4a90e2; }
  .stat-label { display: block; font-size: 22rpx; color: #999; margin-top: 8rpx; }
}

.radar-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-bottom: 24rpx;
  .card-title { display: block; font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .ability-item {
    display: flex; align-items: center; margin-bottom: 20rpx;
    .ability-name { width: 160rpx; font-size: 26rpx; color: #555; }
    .ability-bar-wrap { flex: 1; height: 20rpx; background: #f0f0f0; border-radius: 10rpx; overflow: hidden; margin: 0 16rpx; }
    .ability-bar { height: 100%; border-radius: 10rpx; transition: width 0.5s ease; }
    .ability-score { width: 60rpx; text-align: right; font-size: 26rpx; font-weight: bold; color: #333; }
  }
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
