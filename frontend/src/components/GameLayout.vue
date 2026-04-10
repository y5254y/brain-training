<template>
  <view class="game-layout">
    <view class="game-header" :style="{ background: headerGradient }">
      <view class="header-top">
        <view class="back-btn" @click="goBack">
          <text class="back-icon">‹</text>
        </view>
        <text class="game-title">{{ title }}</text>
        <view class="mode-toggle" v-if="showModeToggle">
          <text
            class="mode-btn"
            :class="{ active: !isPractice }"
            @click="$emit('update:isPractice', false)"
          >正式</text>
          <text
            class="mode-btn"
            :class="{ active: isPractice }"
            @click="$emit('update:isPractice', true)"
          >练习</text>
        </view>
      </view>
      <text class="game-desc">{{ description }}</text>
    </view>

    <view class="difficulty-section" v-if="showDifficulty && gameState === 'idle'">
      <text class="section-label">选择难度</text>
      <view class="difficulty-row">
        <view
          v-for="d in difficulties"
          :key="d.level"
          class="difficulty-btn"
          :class="{ active: selectedDifficulty === d.level, recommended: recommendedDifficulty === d.level }"
          @click="$emit('update:selectedDifficulty', d.level)"
        >
          <text class="diff-name">{{ d.name }}</text>
          <text class="diff-desc">{{ d.desc }}</text>
          <text class="diff-recommend" v-if="recommendedDifficulty === d.level">推荐</text>
        </view>
      </view>
      <button class="start-btn" :style="{ background: headerGradient }" @click="$emit('start')">
        {{ isPractice ? '练习模式开始' : '开始游戏' }}
      </button>
    </view>

    <view class="game-info-bar" v-if="gameState === 'playing'">
      <slot name="info-bar"></slot>
      <text class="practice-badge" v-if="isPractice">练习模式</text>
    </view>

    <view class="game-content" v-if="gameState === 'playing' || gameState === 'preview'">
      <slot></slot>
    </view>

    <view class="result-section" v-if="gameState === 'finished'">
      <text class="result-title">{{ isPractice ? '练习完成！' : '🎉 游戏完成！' }}</text>
      <view class="stars-row" v-if="!isPractice">
        <text
          v-for="n in 3"
          :key="n"
          class="star"
          :class="{ lit: n <= starRating }"
        >★</text>
      </view>
      <text class="result-score" v-if="!isPractice">得分：{{ score }}</text>
      <text class="practice-tip" v-else>练习模式不计分，继续加油！</text>
      <slot name="result-stats"></slot>
      <view class="result-btns">
        <button class="result-btn retry-btn" :style="{ background: headerGradient }" @click="$emit('retry')">再玩一次</button>
        <button class="result-btn back-btn" @click="goBack">返回首页</button>
      </view>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  headerGradient: { type: String, default: 'linear-gradient(135deg, #4a90e2, #7ec8e3)' },
  gameState: { type: String, default: 'idle' },
  isPractice: { type: Boolean, default: false },
  showModeToggle: { type: Boolean, default: true },
  showDifficulty: { type: Boolean, default: true },
  difficulties: { type: Array, default: () => [] },
  selectedDifficulty: { type: Number, default: 1 },
  recommendedDifficulty: { type: Number, default: null },
  score: { type: Number, default: 0 },
  starRating: { type: Number, default: 0 },
})

defineEmits(['update:isPractice', 'update:selectedDifficulty', 'start', 'retry'])

const goBack = () => {
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style lang="scss" scoped>
.game-layout {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

.game-header {
  padding: 30rpx 24rpx 24rpx;
  color: #fff;

  .header-top {
    display: flex;
    align-items: center;
    margin-bottom: 10rpx;
  }

  .back-btn {
    width: 60rpx;
    .back-icon { font-size: 48rpx; color: #fff; font-weight: bold; }
  }

  .game-title {
    flex: 1;
    font-size: 38rpx;
    font-weight: bold;
    text-align: center;
  }

  .mode-toggle {
    display: flex;
    background: rgba(255,255,255,0.25);
    border-radius: 30rpx;
    padding: 4rpx;

    .mode-btn {
      padding: 8rpx 20rpx;
      font-size: 22rpx;
      border-radius: 26rpx;
      color: rgba(255,255,255,0.8);

      &.active {
        background: rgba(255,255,255,0.9);
        color: #333;
        font-weight: bold;
      }
    }
  }

  .game-desc {
    display: block;
    font-size: 26rpx;
    opacity: 0.9;
    text-align: center;
  }
}

.difficulty-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin: 24rpx;

  .section-label {
    display: block;
    font-size: 30rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 20rpx;
  }

  .difficulty-row {
    display: flex;
    gap: 16rpx;
    margin-bottom: 30rpx;
  }

  .difficulty-btn {
    flex: 1;
    border: 2rpx solid #e8e8e8;
    border-radius: 16rpx;
    padding: 20rpx 12rpx;
    text-align: center;
    position: relative;

    &.active {
      border-color: #4a90e2;
      background: rgba(74, 144, 226, 0.1);
    }

    &.recommended {
      border-color: #52c41a;
    }

    .diff-name { display: block; font-size: 28rpx; font-weight: bold; color: #333; }
    .diff-desc { display: block; font-size: 22rpx; color: #999; margin-top: 4rpx; }
    .diff-recommend {
      position: absolute;
      top: -10rpx;
      right: -6rpx;
      background: #52c41a;
      color: #fff;
      font-size: 18rpx;
      padding: 2rpx 10rpx;
      border-radius: 10rpx;
    }
  }

  .start-btn {
    width: 100%;
    height: 90rpx;
    color: #fff;
    font-size: 34rpx;
    font-weight: bold;
    border-radius: 50rpx;
    border: none;
  }
}

.game-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx 24rpx;
  margin: 0 24rpx 16rpx;
  font-size: 26rpx;
  color: #555;

  .practice-badge {
    background: #faad14;
    color: #333;
    font-size: 22rpx;
    padding: 4rpx 16rpx;
    border-radius: 20rpx;
    font-weight: bold;
  }
}

.game-content {
  padding: 0 24rpx;
}

.result-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  margin: 24rpx;
  text-align: center;

  .result-title {
    display: block;
    font-size: 44rpx;
    font-weight: bold;
    margin-bottom: 16rpx;
  }

  .stars-row {
    display: flex;
    justify-content: center;
    gap: 8rpx;
    margin-bottom: 20rpx;

    .star {
      font-size: 60rpx;
      color: #ddd;
      &.lit { color: #f5c518; }
    }
  }

  .result-score {
    display: block;
    font-size: 56rpx;
    font-weight: bold;
    color: #4a90e2;
    margin-bottom: 20rpx;
  }

  .practice-tip {
    display: block;
    font-size: 30rpx;
    color: #faad14;
    margin-bottom: 20rpx;
  }

  .result-btns {
    display: flex;
    gap: 20rpx;
    margin-top: 30rpx;

    .result-btn {
      flex: 1;
      height: 88rpx;
      border-radius: 50rpx;
      font-size: 30rpx;
      border: none;
      color: #fff;
    }

    .back-btn {
      background: #f5f5f5;
      color: #333;
    }
  }
}
</style>
