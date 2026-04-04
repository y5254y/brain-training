/**
 * 用户状态管理 Store
 * 使用 Pinia 管理用户登录状态、用户信息等
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useUserStore = defineStore('user', () => {
  // 用户信息
  const userInfo = ref(null)
  // JWT Token
  const token = ref('')

  // 是否已登录
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

  /**
   * 初始化用户状态（从本地存储读取）
   */
  const initUser = () => {
    try {
      const savedToken = uni.getStorageSync('token')
      const savedUserInfo = uni.getStorageSync('userInfo')
      if (savedToken) {
        token.value = savedToken
      }
      if (savedUserInfo) {
        userInfo.value = JSON.parse(savedUserInfo)
      }
    } catch (e) {
      console.error('初始化用户状态失败', e)
    }
  }

  /**
   * 用户登录
   * @param {string} username - 用户名
   * @param {string} password - 密码
   */
  const login = async (username, password) => {
    const res = await request.post('/auth/login', { username, password })
    token.value = res.access_token
    userInfo.value = res.user
    // 持久化到本地存储
    uni.setStorageSync('token', res.access_token)
    uni.setStorageSync('userInfo', JSON.stringify(res.user))
    return res
  }

  /**
   * 用户注册
   * @param {object} userData - 注册数据
   */
  const register = async (userData) => {
    const res = await request.post('/auth/register', userData)
    // 注册成功后自动登录
    await login(userData.username, userData.password)
    return res
  }

  /**
   * 退出登录
   */
  const logout = () => {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('token')
    uni.removeStorageSync('userInfo')
  }

  /**
   * 更新用户信息
   * @param {object} updateData - 要更新的数据
   */
  const updateUserInfo = async (updateData) => {
    const res = await request.put('/auth/me', updateData)
    userInfo.value = res
    uni.setStorageSync('userInfo', JSON.stringify(res))
    return res
  }

  return {
    userInfo,
    token,
    isLoggedIn,
    initUser,
    login,
    register,
    logout,
    updateUserInfo,
  }
})
