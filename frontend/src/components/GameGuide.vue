<template>
  <view class="guide-overlay" v-if="visible" @click="nextStep">
    <view class="guide-content" @click.stop>
      <text class="guide-icon">{{ steps[currentStep]?.icon || '📖' }}</text>
      <text class="guide-title">{{ steps[currentStep]?.title || '' }}</text>
      <text class="guide-desc">{{ steps[currentStep]?.desc || '' }}</text>
      <view class="guide-animation" v-if="steps[currentStep]?.animation">
        <text class="anim-emoji">{{ steps[currentStep].animation }}</text>
      </view>
      <view class="guide-footer">
        <text class="guide-step">{{ currentStep + 1 }} / {{ steps.length }}</text>
        <view class="guide-btns">
          <text class="guide-skip" @click="skip">跳过</text>
          <text class="guide-next" @click="nextStep">
            {{ currentStep < steps.length - 1 ? '下一步' : '开始游戏' }}
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  steps: { type: Array, default: () => [] },
  storageKey: { type: String, default: '' },
})

const emit = defineEmits(['close', 'complete'])

const currentStep = ref(0)

const nextStep = () => {
  if (currentStep.value < props.steps.length - 1) {
    currentStep.value++
  } else {
    complete()
  }
}

const skip = () => {
  complete()
}

const complete = () => {
  if (props.storageKey) {
    try {
      uni.setStorageSync(props.storageKey, '1')
    } catch (e) {}
  }
  currentStep.value = 0
  emit('complete')
  emit('close')
}

const reset = () => {
  currentStep.value = 0
}

defineExpose({ reset })
</script>

<style lang="scss" scoped>
.guide-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.guide-content {
  background: #fff;
  border-radius: 24rpx;
  padding: 50rpx 40rpx 40rpx;
  width: 600rpx;
  text-align: center;
  animation: guide-in 0.3s ease-out;

  .guide-icon {
    font-size: 80rpx;
    display: block;
    margin-bottom: 20rpx;
  }

  .guide-title {
    display: block;
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 16rpx;
  }

  .guide-desc {
    display: block;
    font-size: 28rpx;
    color: #666;
    line-height: 1.6;
    margin-bottom: 24rpx;
  }

  .guide-animation {
    margin-bottom: 24rpx;
    .anim-emoji {
      font-size: 60rpx;
      animation: guide-bounce 1s infinite;
    }
  }

  .guide-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1rpx solid #f0f0f0;
    padding-top: 24rpx;

    .guide-step {
      font-size: 24rpx;
      color: #999;
    }

    .guide-btns {
      display: flex;
      gap: 24rpx;
    }

    .guide-skip {
      font-size: 28rpx;
      color: #999;
      padding: 10rpx 20rpx;
    }

    .guide-next {
      font-size: 28rpx;
      color: #fff;
      background: #4a90e2;
      padding: 10rpx 30rpx;
      border-radius: 30rpx;
      font-weight: bold;
    }
  }
}

@keyframes guide-in {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes guide-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20rpx); }
}
</style>
