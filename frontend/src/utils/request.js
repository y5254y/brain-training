/**
 * HTTP 请求封装工具
 * 基于 uni.request 封装，支持 Token 拦截器、请求/响应拦截
 */
import { BASE_URL } from './config'

/**
 * 获取存储的 Token
 */
const getToken = () => {
  try {
    return uni.getStorageSync('token') || ''
  } catch (e) {
    return ''
  }
}

/**
 * 基础请求方法
 * @param {string} url - 请求路径（相对于 BASE_URL）
 * @param {string} method - 请求方法（GET/POST/PUT/DELETE）
 * @param {object} data - 请求数据
 * @param {object} options - 额外配置
 */
const request = (url, method = 'GET', data = {}, options = {}) => {
  return new Promise((resolve, reject) => {
    const fullUrl = `${BASE_URL}${url}`
    const token = getToken()

    // 请求头配置
    const header = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    // 如果有 Token，自动添加到请求头（Token 请求拦截）
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: fullUrl,
      method,
      data,
      header,
      timeout: options.timeout || 30000,
      success: (res) => {
        // 响应拦截：处理 HTTP 状态码
        if (res.statusCode === 200 || res.statusCode === 201) {
          // 请求成功，直接返回数据
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // Token 过期或未授权，清除本地 Token 并跳转到登录页
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none',
          })
          setTimeout(() => {
            uni.navigateTo({ url: '/pages/login/login' })
          }, 1500)
          reject(new Error('登录已过期'))
        } else if (res.statusCode === 403) {
          reject(new Error('没有权限执行此操作'))
        } else if (res.statusCode === 404) {
          reject(new Error('请求的资源不存在'))
        } else if (res.statusCode === 422) {
          // FastAPI 数据校验错误
          const detail = res.data?.detail
          const errorMsg = Array.isArray(detail)
            ? detail.map((d) => d.msg).join('; ')
            : detail || '请求数据格式错误'
          reject(new Error(errorMsg))
        } else if (res.statusCode >= 500) {
          reject(new Error('服务器内部错误，请稍后重试'))
        } else {
          const errorMsg = res.data?.detail || res.data?.message || `请求失败（${res.statusCode}）`
          reject(new Error(errorMsg))
        }
      },
      fail: (err) => {
        // 网络错误处理
        console.error('网络请求失败:', err)
        reject(new Error('网络请求失败，请检查网络连接'))
      },
    })
  })
}

// 封装常用的 HTTP 方法
const http = {
  /**
   * GET 请求
   * @param {string} url
   * @param {object} params - 查询参数（会拼接到 URL）
   */
  get: (url, { params, ...options } = {}) => {
    let fullUrl = url
    if (params && Object.keys(params).length) {
      const query = Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== null)        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&')
      if (query) fullUrl += `?${query}`
    }
    return request(fullUrl, 'GET', {}, options)
  },

  /**
   * POST 请求
   * @param {string} url
   * @param {object} data - 请求体数据
   */
  post: (url, data = {}, options = {}) => {
    return request(url, 'POST', data, options)
  },

  /**
   * PUT 请求
   * @param {string} url
   * @param {object} data - 请求体数据
   */
  put: (url, data = {}, options = {}) => {
    return request(url, 'PUT', data, options)
  },

  /**
   * DELETE 请求
   * @param {string} url
   */
  delete: (url, options = {}) => {
    return request(url, 'DELETE', {}, options)
  },
}

export default http
