<template>
  <view class="page-container">
    <NavBar title="设置" />

    <view class="settings-card card">
      <text class="card-title">🎨 显示设置</text>
      <view class="setting-item">
        <text class="setting-label">字体大小</text>
        <view class="font-size-options">
          <view
            v-for="size in fontSizes"
            :key="size.value"
            class="font-size-btn"
            :class="{ active: currentFontSize === size.value }"
            @click="setFontSize(size.value)"
          >
            <text :style="{ fontSize: size.preview }">{{ size.label }}</text>
          </view>
        </view>
      </view>
      <view class="setting-item">
        <text class="setting-label">高对比度模式</text>
        <switch :checked="highContrast" @change="toggleHighContrast" color="#4a90e2" />
      </view>
    </view>

    <view class="settings-card card">
      <text class="card-title">⏰ 提醒设置</text>
      <view class="setting-item">
        <text class="setting-label">每日训练提醒</text>
        <switch :checked="reminderEnabled" @change="toggleReminder" color="#4a90e2" />
      </view>
      <view class="setting-item" v-if="reminderEnabled">
        <text class="setting-label">提醒时间</text>
        <picker mode="time" :value="reminderTime" @change="setReminderTime">
          <text class="time-picker">{{ reminderTime || '09:00' }}</text>
        </picker>
      </view>
    </view>

    <view class="settings-card card">
      <text class="card-title">ℹ️ 关于</text>
      <view class="setting-item">
        <text class="setting-label">版本号</text>
        <text class="setting-value">2.0.0</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import NavBar from '@/components/NavBar.vue'

const userStore = useUserStore()

const currentFontSize = ref('normal')
const highContrast = ref(false)
const reminderEnabled = ref(false)
const reminderTime = ref('09:00')

const fontSizes = [
  { value: 'normal', label: '标准', preview: '28rpx' },
  { value: 'large', label: '大', preview: '34rpx' },
  { value: 'xlarge', label: '特大', preview: '40rpx' },
]

const setFontSize = async (size) => {
  currentFontSize.value = size
  try {
    uni.setStorageSync('fontSize', size)
    if (userStore.isLoggedIn) {
      await request.put('/auth/me', { font_size: size })
      userStore.updateUserInfo({ font_size: size })
    }
  } catch (e) {}
}

const toggleHighContrast = async (e) => {
  highContrast.value = e.detail.value
  try {
    uni.setStorageSync('highContrast', highContrast.value ? '1' : '0')
    if (userStore.isLoggedIn) {
      await request.put('/auth/me', { high_contrast: highContrast.value ? 1 : 0 })
    }
  } catch (e) {}
}

const toggleReminder = (e) => {
  reminderEnabled.value = e.detail.value
  uni.setStorageSync('reminderEnabled', reminderEnabled.value ? '1' : '0')
}

const setReminderTime = async (e) => {
  reminderTime.value = e.detail.value
  try {
    uni.setStorageSync('reminderTime', reminderTime.value)
    if (userStore.isLoggedIn) {
      await request.put('/auth/me', { reminder_time: reminderTime.value })
    }
  } catch (e) {}
}

onMounted(() => {
  try {
    currentFontSize.value = uni.getStorageSync('fontSize') || userStore.userInfo?.font_size || 'normal'
    highContrast.value = (uni.getStorageSync('highContrast') || userStore.userInfo?.high_contrast || 0) == 1
    reminderEnabled.value = uni.getStorageSync('reminderEnabled') === '1'
    reminderTime.value = uni.getStorageSync('reminderTime') || userStore.userInfo?.reminder_time || '09:00'
  } catch (e) {}
})
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 0 24rpx 40rpx; }

.settings-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-top: 20rpx;
  .card-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
}

.setting-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20rpx 0; border-bottom: 1rpx solid #f5f5f5;
  &:last-child { border-bottom: none; }
  .setting-label { font-size: 28rpx; color: #333; }
  .setting-value { font-size: 28rpx; color: #999; }
}

.font-size-options {
  display: flex; gap: 12rpx;
  .font-size-btn {
    padding: 10rpx 24rpx; border-radius: 20rpx; background: #f5f5f5;
    &.active { background: #4a90e2; color: #fff; }
  }
}

.time-picker {
  font-size: 28rpx; color: #4a90e2; padding: 8rpx 20rpx;
  background: rgba(74,144,226,0.1); border-radius: 16rpx;
}
</style>
