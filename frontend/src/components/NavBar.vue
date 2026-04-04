<template>
  <!-- 自定义顶部导航栏组件 -->
  <view class="navbar" :style="{ backgroundColor: bgColor || '#4a90e2' }">
    <!-- 左侧返回按钮 -->
    <view class="nav-left" @click="handleBack" v-if="showBack">
      <text class="back-icon">‹</text>
    </view>
    <view class="nav-left-placeholder" v-else></view>

    <!-- 标题 -->
    <text class="nav-title" :style="{ color: titleColor || '#fff' }">{{ title }}</text>

    <!-- 右侧操作区 -->
    <view class="nav-right">
      <slot name="right"></slot>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({
  // 导航栏标题
  title: {
    type: String,
    default: '脑力锻炼',
  },
  // 是否显示返回按钮
  showBack: {
    type: Boolean,
    default: true,
  },
  // 背景颜色
  bgColor: {
    type: String,
    default: '#4a90e2',
  },
  // 标题颜色
  titleColor: {
    type: String,
    default: '#ffffff',
  },
})

// 处理返回
const handleBack = () => {
  uni.navigateBack()
}
</script>

<style lang="scss" scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  padding: 0 24rpx;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
}

.nav-left,
.nav-left-placeholder {
  width: 60rpx;
}

.back-icon {
  font-size: 48rpx;
  color: #fff;
  font-weight: bold;
  line-height: 88rpx;
}

.nav-title {
  flex: 1;
  text-align: center;
  font-size: 34rpx;
  font-weight: bold;
}

.nav-right {
  width: 60rpx;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
</style>
