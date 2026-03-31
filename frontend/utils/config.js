/**
 * 全局配置文件
 * 包含 API 基础地址等全局配置
 */

// API 基础地址，根据运行环境自动切换
const BASE_URL = (() => {
  // #ifdef H5
  // H5 环境下使用代理或直连
  return 'http://localhost:8000/api/v1'
  // #endif

  // #ifdef MP-WEIXIN
  // 微信小程序环境（需在小程序后台配置合法域名）
  return 'https://your-domain.com/api/v1'
  // #endif

  // 默认（App 等环境）
  return 'http://localhost:8000/api/v1'
})()

const config = {
  // API 基础地址
  BASE_URL,

  // 请求超时时间（毫秒）
  TIMEOUT: 30000,

  // 应用名称
  APP_NAME: '脑力锻炼',

  // 版本号
  VERSION: '1.0.0',
}

export default config
export { BASE_URL }
