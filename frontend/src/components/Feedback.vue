<template>
  <view class="feedback-overlay" v-if="visible" :class="type">
    <view class="feedback-content" :class="[type, { 'animate-in': animating }]">
      <text class="feedback-icon">{{ type === 'correct' ? '✅' : '❌' }}</text>
      <text class="feedback-text">{{ type === 'correct' ? '正确！' : '再想想' }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  type: { type: String, default: 'correct' },
  visible: { type: Boolean, default: false },
  duration: { type: Number, default: 800 },
})

const animating = ref(false)

watch(() => props.visible, (val) => {
  if (val) {
    animating.value = true
    try {
      if (props.type === 'correct') {
        uni.vibrateShort({ type: 'light' })
      } else {
        uni.vibrateShort({ type: 'heavy' })
      }
    } catch (e) {}
  }
})
</script>

<style lang="scss" scoped>
.feedback-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  pointer-events: none;

  &.correct {
    background: rgba(82, 196, 26, 0.1);
  }

  &.wrong {
    background: rgba(255, 77, 79, 0.1);
  }
}

.feedback-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 60rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.2);

  &.animate-in {
    animation: feedback-pop 0.4s ease-out;
  }

  &.correct {
    border: 4rpx solid #52c41a;
  }

  &.wrong {
    border: 4rpx solid #ff4d4f;
  }

  .feedback-icon {
    font-size: 80rpx;
    margin-bottom: 12rpx;
  }

  .feedback-text {
    font-size: 32rpx;
    font-weight: bold;
  }

  &.correct .feedback-text { color: #52c41a; }
  &.wrong .feedback-text { color: #ff4d4f; }
}

@keyframes feedback-pop {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
