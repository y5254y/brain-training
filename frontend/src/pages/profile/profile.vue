<template>
  <view class="page-container">
    <view class="login-tip card" v-if="!userStore.isLoggedIn">
      <text class="logo">🧠</text>
      <text class="tip-text">登录后查看个人中心</text>
      <button class="go-login-btn" @click="goLogin">去登录</button>
    </view>

    <template v-else>
      <view class="user-card">
        <view class="avatar-wrap">
          <image class="avatar" :src="userStore.userInfo.avatar || '/static/default-avatar.png'" mode="aspectFill" />
        </view>
        <view class="user-info">
          <text class="nickname">{{ userStore.userInfo.nickname || userStore.userInfo.username }}</text>
          <text class="age-group-tag">{{ ageGroupLabel }}</text>
        </view>
        <view class="edit-btn" @click="showEditModal = true">✏️ 编辑</view>
      </view>

      <view class="stats-card card">
        <text class="card-title">📊 训练统计</text>
        <view class="stats-grid">
          <view class="stat-item" v-for="stat in statsItems" :key="stat.key">
            <text class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</text>
            <text class="stat-label">{{ stat.label }}</text>
          </view>
        </view>
      </view>

      <view class="menu-card card">
        <view v-for="menu in menus" :key="menu.key" class="menu-item" @click="menu.action()">
          <text class="menu-icon">{{ menu.icon }}</text>
          <text class="menu-label">{{ menu.label }}</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </template>

    <view class="edit-modal" v-if="showEditModal" @click="showEditModal = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">编辑资料</text>
        <view class="form-item">
          <text class="form-label">昵称</text>
          <input class="form-input" v-model="editForm.nickname" placeholder="输入昵称" />
        </view>
        <view class="form-item">
          <text class="form-label">年龄段</text>
          <view class="age-options">
            <view
              v-for="ag in ageGroups"
              :key="ag.value"
              class="age-btn"
              :class="{ active: editForm.age_group === ag.value }"
              @click="editForm.age_group = ag.value"
            >
              <text>{{ ag.label }}</text>
            </view>
          </view>
        </view>
        <button class="save-btn" @click="saveProfile">保存</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()
const showEditModal = ref(false)
const statsData = ref({})
const editForm = ref({ nickname: '', age_group: 'youth' })

const ageGroupMap = { youth: '青少年', middle: '中年', elder: '老年' }
const ageGroupLabel = computed(() => ageGroupMap[userStore.userInfo?.age_group] || '未设置')

const ageGroups = [
  { value: 'youth', label: '青少年' },
  { value: 'middle', label: '中年' },
  { value: 'elder', label: '老年' },
]

const statsItems = computed(() => [
  { key: 'total', label: '总训练次数', value: statsData.value.totalCount || 0, color: '#4a90e2' },
  { key: 'duration', label: '总时长(分)', value: Math.round((statsData.value.totalDuration || 0) / 60), color: '#52c41a' },
  { key: 'streak', label: '连续天数', value: statsData.value.streakDays || 0, color: '#faad14' },
  { key: 'types', label: '训练类型', value: statsData.value.typeCount || 0, color: '#722ed1' },
])

const menus = [
  { key: 'family', icon: '👨‍👩‍👧', label: '家人关注', action: () => uni.navigateTo({ url: '/pages/family/index' }) },
  { key: 'achievement', icon: '🏆', label: '我的成就', action: () => uni.navigateTo({ url: '/pages/achievement/achievement' }) },
  { key: 'settings', icon: '⚙️', label: '设置', action: () => uni.navigateTo({ url: '/pages/settings/settings' }) },
  { key: 'about', icon: 'ℹ️', label: '关于应用', action: () => uni.showToast({ title: '脑力锻炼 v2.0.0', icon: 'none' }) },
]

const loadStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const stats = await request.get('/training/stats')
    const byType = stats.by_type || {}
    statsData.value = {
      totalCount: stats.total_count || 0,
      totalDuration: stats.total_duration || 0,
      streakDays: stats.streak_days || 0,
      typeCount: Object.keys(byType).length,
    }
  } catch (e) {}
}

const saveProfile = async () => {
  try {
    await userStore.updateUserInfo({
      nickname: editForm.value.nickname,
      age_group: editForm.value.age_group,
    })
    showEditModal.value = false
    uni.showToast({ title: '保存成功', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}

const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })

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
  editForm.value = {
    nickname: userStore.userInfo?.nickname || '',
    age_group: userStore.userInfo?.age_group || 'youth',
  }
})
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 0 0 40rpx; }

.login-tip {
  margin: 100rpx 40rpx; background: #fff; border-radius: 20rpx; padding: 80rpx 40rpx; text-align: center;
  .logo { display: block; font-size: 100rpx; margin-bottom: 24rpx; }
  .tip-text { display: block; font-size: 30rpx; color: #999; margin-bottom: 40rpx; }
  .go-login-btn { background: #4a90e2; color: #fff; border-radius: 50rpx; padding: 22rpx 80rpx; font-size: 30rpx; border: none; }
}

.user-card {
  background: linear-gradient(135deg, #4a90e2, #7ec8e3);
  padding: 60rpx 40rpx 80rpx; display: flex; align-items: center; gap: 24rpx;
  .avatar-wrap { .avatar { width: 120rpx; height: 120rpx; border-radius: 60rpx; border: 4rpx solid rgba(255,255,255,0.7); } }
  .user-info { flex: 1; .nickname { display: block; font-size: 36rpx; font-weight: bold; color: #fff; margin-bottom: 8rpx; } .age-group-tag { display: inline-block; background: rgba(255,255,255,0.25); color: #fff; font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 20rpx; } }
  .edit-btn { font-size: 24rpx; color: rgba(255,255,255,0.85); }
}

.stats-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx;
  margin: -40rpx 24rpx 24rpx; box-shadow: 0 8rpx 30rpx rgba(0,0,0,0.1);
  .card-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 24rpx; }
  .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24rpx; }
  .stat-item { text-align: center; background: #fafafa; border-radius: 16rpx; padding: 24rpx; }
  .stat-value { display: block; font-size: 44rpx; font-weight: bold; margin-bottom: 8rpx; }
  .stat-label { display: block; font-size: 22rpx; color: #999; }
}

.menu-card {
  background: #fff; border-radius: 20rpx; padding: 0 24rpx; margin: 0 24rpx 24rpx;
  .menu-item {
    display: flex; align-items: center; padding: 28rpx 0; border-bottom: 1rpx solid #f0f0f0;
    &:last-child { border-bottom: none; }
    .menu-icon { font-size: 36rpx; margin-right: 20rpx; }
    .menu-label { flex: 1; font-size: 30rpx; color: #333; }
    .menu-arrow { font-size: 36rpx; color: #ccc; }
  }
}

.logout-btn {
  margin: 0 40rpx; background: #fff; color: #ff4d4f; border: 2rpx solid #ff4d4f;
  border-radius: 50rpx; height: 88rpx; font-size: 30rpx;
}

.edit-modal {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 9999;
  .modal-content {
    background: #fff; border-radius: 24rpx; padding: 40rpx; width: 600rpx;
    .modal-title { display: block; font-size: 34rpx; font-weight: bold; text-align: center; margin-bottom: 30rpx; }
    .form-item { margin-bottom: 24rpx; }
    .form-label { display: block; font-size: 28rpx; color: #333; margin-bottom: 12rpx; }
    .form-input {
      width: 100%; height: 80rpx; border: 2rpx solid #e8e8e8; border-radius: 16rpx; padding: 0 24rpx; font-size: 28rpx;
    }
    .age-options { display: flex; gap: 16rpx; }
    .age-btn {
      flex: 1; padding: 16rpx; text-align: center; border-radius: 16rpx; background: #f5f5f5; font-size: 26rpx;
      &.active { background: #4a90e2; color: #fff; }
    }
    .save-btn {
      width: 100%; height: 88rpx; background: #4a90e2; color: #fff;
      border-radius: 44rpx; font-size: 30rpx; border: none; margin-top: 20rpx;
    }
  }
}
</style>
