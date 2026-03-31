<template>
  <view class="page-container">
    <!-- 未登录 -->
    <view class="login-tip card" v-if="!userStore.isLoggedIn">
      <text class="logo">🧠</text>
      <text class="tip-text">登录后查看个人中心</text>
      <button class="go-login-btn" @click="goLogin">去登录</button>
    </view>

    <!-- 已登录 -->
    <template v-else>
      <!-- 用户信息卡 -->
      <view class="user-card">
        <view class="avatar-wrap">
          <image
            class="avatar"
            :src="userStore.userInfo.avatar || '/static/default-avatar.png'"
            mode="aspectFill"
          />
        </view>
        <view class="user-info">
          <text class="nickname">{{ userStore.userInfo.nickname || userStore.userInfo.username }}</text>
          <text class="age-group-tag">{{ ageGroupLabel }}</text>
        </view>
        <view class="edit-btn" @click="showEditModal = true">✏️ 编辑</view>
      </view>

      <!-- 训练统计 -->
      <view class="stats-card card">
        <text class="card-title">📊 训练统计</text>
        <view class="stats-grid">
          <view class="stat-item" v-for="stat in statsItems" :key="stat.key">
            <text class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</text>
            <text class="stat-label">{{ stat.label }}</text>
          </view>
        </view>
      </view>

      <!-- 功能菜单 -->
      <view class="menu-card card">
        <view
          v-for="menu in menus"
          :key="menu.key"
          class="menu-item"
          @click="menu.action()"
        >
          <text class="menu-icon">{{ menu.icon }}</text>
          <text class="menu-label">{{ menu.label }}</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 退出登录 -->
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </template>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()
const showEditModal = ref(false)
const statsData = ref({})

const ageGroupMap = {
  youth: '青少年',
  middle: '中年',
  elder: '老年',
}

const ageGroupLabel = computed(() => {
  return ageGroupMap[userStore.userInfo?.age_group] || '未设置'
})

const statsItems = computed(() => [
  { key: 'total', label: '总训练次数', value: statsData.value.totalCount || 0, color: '#4a90e2' },
  { key: 'duration', label: '总时长(分)', value: Math.round((statsData.value.totalDuration || 0) / 60), color: '#52c41a' },
  { key: 'memory', label: '记忆力最高分', value: statsData.value.memoryMax || 0, color: '#ff9a9e' },
  { key: 'attention', label: '注意力最高分', value: statsData.value.attentionMax || 0, color: '#a1c4fd' },
])

const menus = [
  {
    key: 'family',
    icon: '👨‍👩‍👧',
    label: '家人关注',
    action: () => uni.showToast({ title: '功能开发中', icon: 'none' }),
  },
  {
    key: 'achievement',
    icon: '🏆',
    label: '我的成就',
    action: () => uni.showToast({ title: '功能开发中', icon: 'none' }),
  },
  {
    key: 'settings',
    icon: '⚙️',
    label: '设置',
    action: () => uni.showToast({ title: '功能开发中', icon: 'none' }),
  },
  {
    key: 'about',
    icon: 'ℹ️',
    label: '关于应用',
    action: () => uni.showToast({ title: '脑力锻炼 v1.0.0', icon: 'none' }),
  },
]

const loadStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const stats = await request.get('/training/stats')
    const byType = stats.by_type || {}
    statsData.value = {
      totalCount: stats.total_count || 0,
      totalDuration: stats.total_duration || 0,
      memoryMax: byType.memory?.max_score || 0,
      attentionMax: byType.attention?.max_score || 0,
    }
  } catch (e) {
    console.log('加载统计失败', e)
  }
}

const goLogin = () => {
  uni.navigateTo({ url: '/pages/login/login' })
}

const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
        uni.reLaunch({ url: '/pages/index/index' })
      }
    },
  })
}

onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 0 0 40rpx;
}

.login-tip {
  margin: 100rpx 40rpx; background: #fff; border-radius: 20rpx; padding: 80rpx 40rpx; text-align: center;
  .logo { display: block; font-size: 100rpx; margin-bottom: 24rpx; }
  .tip-text { display: block; font-size: 30rpx; color: #999; margin-bottom: 40rpx; }
  .go-login-btn { background: #4a90e2; color: #fff; border-radius: 50rpx; padding: 22rpx 80rpx; font-size: 30rpx; border: none; }
}

/* 用户信息卡 */
.user-card {
  background: linear-gradient(135deg, #4a90e2, #7ec8e3);
  padding: 60rpx 40rpx 80rpx;
  display: flex; align-items: center; gap: 24rpx;
  .avatar-wrap {
    .avatar { width: 120rpx; height: 120rpx; border-radius: 60rpx; border: 4rpx solid rgba(255,255,255,0.7); }
  }
  .user-info {
    flex: 1;
    .nickname { display: block; font-size: 36rpx; font-weight: bold; color: #fff; margin-bottom: 8rpx; }
    .age-group-tag { display: inline-block; background: rgba(255,255,255,0.25); color: #fff; font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 20rpx; }
  }
  .edit-btn { font-size: 24rpx; color: rgba(255,255,255,0.85); }
}

/* 统计卡片 */
.stats-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx;
  margin: -40rpx 24rpx 24rpx; box-shadow: 0 8rpx 30rpx rgba(0,0,0,0.1);
  .card-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24rpx; }
  .stat-item { text-align: center; background: #fafafa; border-radius: 16rpx; padding: 24rpx; }
  .stat-value { display: block; font-size: 44rpx; font-weight: bold; margin-bottom: 8rpx; }
  .stat-label { display: block; font-size: 22rpx; color: #999; }
}

/* 菜单 */
.menu-card {
  background: #fff; border-radius: 20rpx; padding: 0 24rpx; margin: 0 24rpx 24rpx;
  .menu-item {
    display: flex; align-items: center; padding: 28rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
    &:last-child { border-bottom: none; }
    .menu-icon { font-size: 36rpx; margin-right: 20rpx; }
    .menu-label { flex: 1; font-size: 30rpx; color: #333; }
    .menu-arrow { font-size: 36rpx; color: #ccc; }
  }
}

.logout-btn {
  margin: 0 40rpx;
  background: #fff; color: #ff4d4f; border: 2rpx solid #ff4d4f;
  border-radius: 50rpx; height: 88rpx; font-size: 30rpx;
}
</style>
