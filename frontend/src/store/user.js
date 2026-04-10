/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    userInfo: JSON.parse(uni.getStorageSync('userInfo') || '{}'),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(username, password) {
      const res = await request.post('/auth/login', { username, password })
      this.token = res.access_token
      this.userInfo = res.user
      uni.setStorageSync('token', this.token)
      uni.setStorageSync('userInfo', JSON.stringify(res.user))
    },

    async updateUserInfo(data) {
      const res = await request.put('/auth/me', data)
      this.userInfo = { ...this.userInfo, ...res }
      uni.setStorageSync('userInfo', JSON.stringify(this.userInfo))
    },

    async fetchUserInfo() {
      try {
        const res = await request.get('/auth/me')
        this.userInfo = res
        uni.setStorageSync('userInfo', JSON.stringify(res))
      } catch (e) {}
    },

    logout() {
      this.token = ''
      this.userInfo = {}
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
    },
  },
})
