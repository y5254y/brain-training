<template>
  <view class="page-container">
    <NavBar title="我的成就" />
    <view class="achievement-summary">
      <text class="summary-icon">🏆</text>
      <text class="summary-text">已解锁 {{ unlockedCount }} / {{ totalCount }}</text>
      <view class="progress-bar">
        <view class="progress-fill" :style="{ width: `${progressPercent}%` }"></view>
      </view>
    </view>

    <view class="achievement-grid">
      <view
        v-for="ach in achievements"
        :key="ach.key"
        class="achievement-card"
        :class="{ unlocked: ach.unlocked }"
      >
        <text class="ach-icon">{{ ach.unlocked ? ach.icon : '🔒' }}</text>
        <text class="ach-name">{{ ach.name }}</text>
        <text class="ach-desc">{{ ach.desc }}</text>
        <text class="ach-date" v-if="ach.unlocked">{{ formatDate(ach.unlocked_at) }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import NavBar from '@/components/NavBar.vue'

const userStore = useUserStore()
const achievements = ref([])
const unlockedCount = computed(() => achievements.value.filter(a => a.unlocked).length)
const totalCount = computed(() => achievements.value.length)
const progressPercent = computed(() => totalCount.value > 0 ? Math.round(unlockedCount.value / totalCount.value * 100) : 0)

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth()+1}/${d.getDate()} 解锁`
}

const loadAchievements = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/achievement/list')
    achievements.value = res.achievements || []
  } catch (e) {}
}

onMounted(() => { loadAchievements() })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 0 24rpx 40rpx; }

.achievement-summary {
  background: linear-gradient(135deg, #f5c518, #f0ad4e);
  border-radius: 20rpx; padding: 40rpx; margin-top: 20rpx; text-align: center; margin-bottom: 24rpx;
  .summary-icon { display: block; font-size: 80rpx; margin-bottom: 12rpx; }
  .summary-text { display: block; font-size: 34rpx; font-weight: bold; color: #333; margin-bottom: 16rpx; }
  .progress-bar { height: 16rpx; background: rgba(255,255,255,0.5); border-radius: 8rpx; overflow: hidden; }
  .progress-fill { height: 100%; background: #333; border-radius: 8rpx; transition: width 0.5s ease; }
}

.achievement-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.achievement-card {
  background: #fff; border-radius: 20rpx; padding: 24rpx; text-align: center;
  box-shadow: 0 4rpx 15rpx rgba(0,0,0,0.06);
  opacity: 0.5;

  &.unlocked { opacity: 1; border: 2rpx solid #f5c518; }

  .ach-icon { display: block; font-size: 56rpx; margin-bottom: 10rpx; }
  .ach-name { display: block; font-size: 28rpx; font-weight: bold; color: #333; margin-bottom: 6rpx; }
  .ach-desc { display: block; font-size: 22rpx; color: #999; margin-bottom: 6rpx; }
  .ach-date { display: block; font-size: 20rpx; color: #f5c518; }
}
</style>
