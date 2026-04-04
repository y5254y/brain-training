<template>
  <view class="login-page">
    <view class="logo-section">
      <text class="logo-icon">🧠</text>
      <text class="logo-title">脑力锻炼</text>
      <text class="logo-subtitle">让大脑更年轻</text>
    </view>

    <!-- 登录表单 -->
    <view class="form-section card">
      <view class="form-item">
        <text class="form-label">用户名</text>
        <input
          v-model="form.username"
          class="form-input"
          placeholder="请输入用户名"
          placeholder-class="input-placeholder"
        />
      </view>

      <view class="form-item">
        <text class="form-label">密码</text>
        <input
          v-model="form.password"
          class="form-input"
          placeholder="请输入密码（至少6位）"
          placeholder-class="input-placeholder"
          password
        />
      </view>

      <!-- 注册时额外的字段 -->
      <template v-if="isRegister">
        <view class="form-item">
          <text class="form-label">昵称</text>
          <input
            v-model="form.nickname"
            class="form-input"
            placeholder="请输入昵称"
            placeholder-class="input-placeholder"
          />
        </view>

        <view class="form-item">
          <text class="form-label">年龄段</text>
          <picker
            :value="ageGroupIndex"
            :range="ageGroups"
            range-key="name"
            @change="onAgeGroupChange"
          >
            <view class="picker-value">
              {{ ageGroups[ageGroupIndex].name }}
            </view>
          </picker>
        </view>
      </template>

      <button
        class="submit-btn"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ isRegister ? '立即注册' : '登录' }}
      </button>

      <view class="toggle-row">
        <text class="toggle-text" @click="toggleMode">
          {{ isRegister ? '已有账号？去登录' : '没有账号？立即注册' }}
        </text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// 表单数据
const form = reactive({
  username: '',
  password: '',
  nickname: '',
  age_group: 'youth',
})

// 是否注册模式
const isRegister = ref(false)
// 加载状态
const loading = ref(false)

// 年龄段选项
const ageGroups = [
  { key: 'youth', name: '青少年（18岁以下）' },
  { key: 'middle', name: '中年（18-59岁）' },
  { key: 'elder', name: '老年（60岁以上）' },
]
const ageGroupIndex = ref(0)

// 切换登录/注册模式
const toggleMode = () => {
  isRegister.value = !isRegister.value
}

// 年龄段选择变化
const onAgeGroupChange = (e) => {
  ageGroupIndex.value = e.detail.value
  form.age_group = ageGroups[e.detail.value].key
}

// 提交表单
const handleSubmit = async () => {
  if (!form.username || !form.password) {
    uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
    return
  }
  if (form.password.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' })
    return
  }

  loading.value = true
  try {
    if (isRegister.value) {
      await userStore.register(form)
      uni.showToast({ title: '注册成功', icon: 'success' })
    } else {
      await userStore.login(form.username, form.password)
      uni.showToast({ title: '登录成功', icon: 'success' })
    }
    // 登录/注册成功后跳转到首页
    setTimeout(() => {
      uni.switchTab({ url: '/pages/index/index' })
    }, 800)
  } catch (err) {
    uni.showToast({
      title: err.message || (isRegister.value ? '注册失败' : '登录失败'),
      icon: 'none',
    })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(160deg, #4a90e2 0%, #7ec8e3 50%, #f5f5f5 100%);
  padding: 80rpx 40rpx 40rpx;
}

/* Logo 区域 */
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;

  .logo-icon {
    font-size: 100rpx;
    margin-bottom: 20rpx;
  }

  .logo-title {
    font-size: 52rpx;
    font-weight: bold;
    color: #fff;
    margin-bottom: 12rpx;
  }

  .logo-subtitle {
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.9);
  }
}

/* 表单区域 */
.form-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.15);
}

.form-item {
  margin-bottom: 30rpx;

  .form-label {
    display: block;
    font-size: 28rpx;
    color: #333;
    margin-bottom: 12rpx;
    font-weight: 500;
  }

  .form-input {
    width: 100%;
    height: 88rpx;
    border: 2rpx solid #e8e8e8;
    border-radius: 12rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
    color: #333;
    background: #fafafa;
    box-sizing: border-box;
  }

  .picker-value {
    height: 88rpx;
    border: 2rpx solid #e8e8e8;
    border-radius: 12rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
    color: #333;
    background: #fafafa;
    display: flex;
    align-items: center;
  }
}

.submit-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(90deg, #4a90e2, #7ec8e3);
  color: #fff;
  font-size: 34rpx;
  font-weight: bold;
  border-radius: 50rpx;
  border: none;
  margin-top: 20rpx;
  margin-bottom: 24rpx;
}

.toggle-row {
  text-align: center;

  .toggle-text {
    font-size: 28rpx;
    color: #4a90e2;
  }
}

.input-placeholder {
  color: #ccc;
}
</style>
