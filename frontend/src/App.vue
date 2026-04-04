<template>
  <!-- 应用根组件 -->
  <view class="app-container">
    <router-view />
  </view>
</template>

<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'

// 应用启动时初始化
onLaunch(() => {
  console.log('脑力锻炼 App 启动')
  // 初始化用户状态
  const userStore = useUserStore()
  userStore.initUser()
})

onShow(() => {
  console.log('App Show')
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style lang="scss">
/* 引入全局样式 */
@import './uni.scss';

/* 全局基础样式 */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

/* 公共容器样式 */
.page-container {
  min-height: 100vh;
  padding: 20rpx;
  box-sizing: border-box;
}

/* 全局按钮样式 */
.btn-primary {
  background-color: #4a90e2;
  color: #fff;
  border-radius: 50rpx;
  padding: 20rpx 40rpx;
  font-size: 32rpx;
  border: none;

  &:active {
    background-color: #357abd;
  }
}

/* 全局卡片样式 */
.card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  margin-bottom: 20rpx;
}
</style>
