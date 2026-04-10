<template>
  <view class="page-container">
    <NavBar title="家人报告" />
    <view class="report-card card" v-if="reportData">
      <view class="member-header">
        <text class="member-name">{{ memberName }}</text>
        <text class="member-status" :class="{ trained: reportData.today_trained }">
          {{ reportData.today_trained ? '✅ 今日已训练' : '⚠️ 今日未训练' }}
        </text>
      </view>

      <view class="alert-section" v-if="reportData.alerts && reportData.alerts.length > 0">
        <view v-for="alert in reportData.alerts" :key="alert.type" class="alert-item" :class="alert.level">
          <text>{{ alert.message }}</text>
        </view>
      </view>

      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">{{ reportData.total_count || 0 }}</text>
          <text class="stat-label">总训练</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ Math.round((reportData.total_duration || 0) / 60) }}</text>
          <text class="stat-label">总分钟</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ reportData.streak_days || 0 }}</text>
          <text class="stat-label">连续天数</text>
        </view>
      </view>

      <text class="section-title">认知能力</text>
      <view class="ability-list">
        <view v-for="(score, key) in reportData.radar_data" :key="key" class="ability-item">
          <text class="ability-name">{{ gameTypeMap[key] || key }}</text>
          <view class="ability-bar-wrap">
            <view class="ability-bar" :style="{ width: `${score}%` }"></view>
          </view>
          <text class="ability-score">{{ score }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import NavBar from '@/components/NavBar.vue'

const reportData = ref(null)
const memberName = ref('')

const gameTypeMap = {
  memory: '🃏 记忆力', attention: '🎯 注意力', calculation: '🔢 计算力',
  logic: '🧩 逻辑推理', language: '💬 语言能力', spatial: '🧭 空间定向',
  face: '👤 人脸识别', rhythm: '🎵 节律训练', classification: '📂 分类归纳',
  dual_task: '🔄 双重任务',
}

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1]
  const userId = page.options?.userId
  memberName.value = page.options?.name || '家人'

  if (userId) {
    loadReport(parseInt(userId))
  }
})

const loadReport = async (userId) => {
  try {
    const res = await request.get(`/family/${userId}/report`)
    reportData.value = res
  } catch (e) {
    uni.showToast({ title: '加载报告失败', icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 0 24rpx 40rpx; }

.report-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-top: 20rpx;
  .member-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
  .member-name { font-size: 36rpx; font-weight: bold; color: #333; }
  .member-status { font-size: 24rpx; padding: 6rpx 16rpx; border-radius: 16rpx;
    &:not(.trained) { background: #fff2f0; color: #ff4d4f; }
    &.trained { background: #f6ffed; color: #52c41a; }
  }
}

.alert-section { margin-bottom: 20rpx; }
.alert-item {
  padding: 16rpx 20rpx; border-radius: 12rpx; margin-bottom: 10rpx; font-size: 26rpx;
  &.warning { background: #fffbe6; color: #d48806; }
  &.danger { background: #fff2f0; color: #cf1322; }
}

.stats-row {
  display: flex; justify-content: space-around; padding: 20rpx 0; margin-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
  .stat-item { text-align: center; }
  .stat-value { display: block; font-size: 40rpx; font-weight: bold; color: #4a90e2; }
  .stat-label { display: block; font-size: 22rpx; color: #999; margin-top: 6rpx; }
}

.section-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 16rpx; }

.ability-item {
  display: flex; align-items: center; margin-bottom: 14rpx;
  .ability-name { width: 160rpx; font-size: 24rpx; color: #555; }
  .ability-bar-wrap { flex: 1; height: 16rpx; background: #f0f0f0; border-radius: 8rpx; overflow: hidden; margin: 0 12rpx; }
  .ability-bar { height: 100%; background: linear-gradient(90deg, #4a90e2, #7ec8e3); border-radius: 8rpx; }
  .ability-score { width: 50rpx; text-align: right; font-size: 24rpx; font-weight: bold; color: #333; }
}
</style>
