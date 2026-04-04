<template>
  <view class="page-container">
    <!-- 顶部欢迎区域 -->
    <view class="welcome-section">
      <text class="welcome-title">🧠 脑力锻炼</text>
      <text class="welcome-subtitle">每天训练，保持大脑活力</text>
      <text class="user-greeting" v-if="userStore.isLoggedIn">
        你好，{{ userStore.userInfo.nickname || userStore.userInfo.username }} 👋
      </text>
    </view>

    <!-- 今日训练统计 -->
    <view class="stats-card card">
      <text class="card-title">📊 今日训练</text>
      <view class="stats-row">
        <view class="stat-item">
          <text class="stat-value">{{ todayStats.count }}</text>
          <text class="stat-label">训练次数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ Math.round(todayStats.duration / 60) }}</text>
          <text class="stat-label">训练分钟</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ todayStats.avgScore }}</text>
          <text class="stat-label">平均分</text>
        </view>
      </view>
    </view>

    <!-- 训练模块入口 -->
    <view class="section-title">🎮 训练模块</view>
    <view class="game-grid">
      <view
        v-for="game in games"
        :key="game.type"
        class="game-card"
        :style="{ backgroundColor: game.color }"
        @click="goToGame(game.path)"
      >
        <text class="game-icon">{{ game.icon }}</text>
        <text class="game-name">{{ game.name }}</text>
        <text class="game-desc">{{ game.desc }}</text>
      </view>
    </view>

    <!-- 快速操作 -->
    <view class="quick-actions">
      <button class="action-btn" @click="goToReport">📈 查看报告</button>
      <button class="action-btn" @click="goToProfile">👤 个人中心</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'

const userStore = useUserStore()

// 今日训练统计数据
const todayStats = ref({
  count: 0,
  duration: 0,
  avgScore: 0,
})

// 训练模块配置
const games = [
  {
    type: 'memory',
    name: '记忆力',
    icon: '🃏',
    desc: '翻牌配对',
    color: '#ff9a9e',
    path: '/pages/train/memory/memory',
  },
  {
    type: 'attention',
    name: '注意力',
    icon: '🎯',
    desc: '舒尔特方格',
    color: '#a1c4fd',
    path: '/pages/train/attention/attention',
  },
  {
    type: 'calculation',
    name: '计算力',
    icon: '🔢',
    desc: '速算挑战',
    color: '#84fab0',
    path: '/pages/train/calculation/calculation',
  },
  {
    type: 'logic',
    name: '逻辑推理',
    icon: '🧩',
    desc: '图形推理',
    color: '#ffecd2',
    path: '/pages/train/logic/logic',
  },
  {
    type: 'language',
    name: '语言能力',
    icon: '💬',
    desc: '成语接龙',
    color: '#d4fc79',
    path: '/pages/train/language/language',
  },
]

// 加载今日训练统计
const loadTodayStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await request.get('/report/daily')
    todayStats.value = {
      count: res.total_count || 0,
      duration: res.total_duration || 0,
      avgScore: 0,
    }
  } catch (e) {
    console.log('加载今日统计失败', e)
  }
}

// 跳转到训练游戏页
const goToGame = (path) => {
  if (!userStore.isLoggedIn) {
    uni.navigateTo({ url: '/pages/login/login' })
    return
  }
  uni.navigateTo({ url: path })
}

// 跳转到报告页
const goToReport = () => {
  uni.switchTab({ url: '/pages/report/report' })
}

// 跳转到个人中心
const goToProfile = () => {
  uni.switchTab({ url: '/pages/profile/profile' })
}

onMounted(() => {
  loadTodayStats()
})
</script>

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 30rpx;
}

/* 欢迎区域 */
.welcome-section {
  background: linear-gradient(135deg, #4a90e2, #7ec8e3);
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 30rpx;
  color: #fff;

  .welcome-title {
    display: block;
    font-size: 48rpx;
    font-weight: bold;
    margin-bottom: 10rpx;
  }

  .welcome-subtitle {
    display: block;
    font-size: 28rpx;
    opacity: 0.9;
    margin-bottom: 10rpx;
  }

  .user-greeting {
    display: block;
    font-size: 26rpx;
    opacity: 0.85;
  }
}

/* 统计卡片 */
.stats-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);

  .card-title {
    display: block;
    font-size: 30rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 24rpx;
  }

  .stats-row {
    display: flex;
    justify-content: space-around;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;

    .stat-value {
      font-size: 48rpx;
      font-weight: bold;
      color: #4a90e2;
    }

    .stat-label {
      font-size: 24rpx;
      color: #999;
      margin-top: 8rpx;
    }
  }
}

/* 训练模块标题 */
.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

/* 游戏卡片网格 */
.game-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.game-card {
  border-radius: 20rpx;
  padding: 30rpx 24rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 15rpx rgba(0, 0, 0, 0.1);

  &:active {
    opacity: 0.85;
  }

  .game-icon {
    font-size: 56rpx;
    margin-bottom: 12rpx;
  }

  .game-name {
    font-size: 30rpx;
    font-weight: bold;
    color: #333;
    margin-bottom: 8rpx;
  }

  .game-desc {
    font-size: 22rpx;
    color: #666;
  }
}

/* 快速操作按钮 */
.quick-actions {
  display: flex;
  gap: 20rpx;

  .action-btn {
    flex: 1;
    background: #fff;
    color: #4a90e2;
    border: 2rpx solid #4a90e2;
    border-radius: 50rpx;
    padding: 22rpx 0;
    font-size: 28rpx;
    text-align: center;

    &:active {
      background: #4a90e2;
      color: #fff;
    }
  }
}
</style>
