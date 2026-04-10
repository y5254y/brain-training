<template>
  <view class="page-container">
    <NavBar title="家人关注" />

    <view class="login-tip card" v-if="!userStore.isLoggedIn">
      <text class="tip-text">请先登录</text>
      <button class="go-login-btn" @click="goLogin">去登录</button>
    </view>

    <template v-else>
      <view class="action-card card">
        <view class="action-btns">
          <button class="invite-btn" @click="generateCode">🔑 生成邀请码</button>
          <button class="bind-btn" @click="showBindModal = true">🔗 输入邀请码绑定</button>
        </view>
        <view class="invite-code-display" v-if="inviteCode">
          <text class="code-label">您的邀请码：</text>
          <text class="code-value">{{ inviteCode }}</text>
          <text class="code-tip">分享给家人，30分钟内有效</text>
        </view>
      </view>

      <view class="family-list card" v-if="familyList.length > 0">
        <text class="section-title">已关注的家人</text>
        <view v-for="member in familyList" :key="member.relation_id" class="family-item">
          <view class="member-info" @click="viewReport(member)">
            <text class="member-avatar">{{ member.avatar || '👤' }}</text>
            <view class="member-detail">
              <text class="member-name">{{ member.nickname || member.username }}</text>
              <text class="member-relation">{{ relationMap[member.relation_type] || member.relation_type }}</text>
            </view>
          </view>
          <view class="member-actions">
            <text class="view-btn" @click="viewReport(member)">📊 报告</text>
            <text class="unbind-btn" @click="unbind(member.relation_id)">解除</text>
          </view>
        </view>
      </view>

      <view class="empty-tip" v-else>
        <text>暂无关注的家人，生成邀请码或输入家人的邀请码来绑定</text>
      </view>
    </template>

    <view class="bind-modal" v-if="showBindModal" @click="showBindModal = false">
      <view class="modal-content" @click.stop>
        <text class="modal-title">输入邀请码</text>
        <input class="code-input" v-model="inputCode" placeholder="请输入6位数字邀请码" maxlength="6" type="number" />
        <button class="modal-confirm" @click="bindFamily">确认绑定</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import request from '@/utils/request'
import NavBar from '@/components/NavBar.vue'

const userStore = useUserStore()
const inviteCode = ref('')
const familyList = ref([])
const showBindModal = ref(false)
const inputCode = ref('')

const relationMap = { child: '子女', spouse: '配偶', caregiver: '护工', other: '其他' }

const generateCode = async () => {
  try {
    const res = await request.post('/family/invite-code')
    inviteCode.value = res.invite_code
  } catch (e) {
    uni.showToast({ title: '生成邀请码失败', icon: 'none' })
  }
}

const bindFamily = async () => {
  if (!inputCode.value || inputCode.value.length !== 6) {
    uni.showToast({ title: '请输入6位邀请码', icon: 'none' })
    return
  }
  try {
    await request.post('/family/bind', { invite_code: inputCode.value })
    uni.showToast({ title: '绑定成功！', icon: 'success' })
    showBindModal.value = false
    inputCode.value = ''
    loadFamilyList()
  } catch (e) {
    uni.showToast({ title: e.message || '绑定失败', icon: 'none' })
  }
}

const loadFamilyList = async () => {
  try {
    const res = await request.get('/family/list')
    familyList.value = res.family_list || []
  } catch (e) {}
}

const viewReport = (member) => {
  uni.navigateTo({ url: `/pages/family/report?userId=${member.user_id}&name=${member.nickname || member.username}` })
}

const unbind = (relationId) => {
  uni.showModal({
    title: '确认解除',
    content: '确定要解除关注吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await request.delete(`/family/unbind/${relationId}`)
          uni.showToast({ title: '已解除', icon: 'success' })
          loadFamilyList()
        } catch (e) {
          uni.showToast({ title: '操作失败', icon: 'none' })
        }
      }
    },
  })
}

const goLogin = () => uni.navigateTo({ url: '/pages/login/login' })

onMounted(() => { if (userStore.isLoggedIn) loadFamilyList() })
</script>

<style lang="scss" scoped>
.page-container { min-height: 100vh; background: #f5f5f5; padding: 0 24rpx 40rpx; }

.login-tip { background: #fff; border-radius: 20rpx; padding: 60rpx; text-align: center; margin-top: 20rpx;
  .tip-text { display: block; font-size: 28rpx; color: #999; margin-bottom: 30rpx; }
  .go-login-btn { background: #4a90e2; color: #fff; border-radius: 50rpx; padding: 20rpx 60rpx; font-size: 28rpx; border: none; }
}

.action-card {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-top: 20rpx;
  .action-btns { display: flex; gap: 20rpx; margin-bottom: 20rpx; }
  .invite-btn, .bind-btn {
    flex: 1; height: 80rpx; border-radius: 40rpx; font-size: 28rpx; border: none;
  }
  .invite-btn { background: #4a90e2; color: #fff; }
  .bind-btn { background: #fff; color: #4a90e2; border: 2rpx solid #4a90e2; }
  .invite-code-display {
    text-align: center; padding: 20rpx; background: #f0f7ff; border-radius: 16rpx;
    .code-label { display: block; font-size: 24rpx; color: #666; margin-bottom: 8rpx; }
    .code-value { display: block; font-size: 56rpx; font-weight: bold; color: #4a90e2; letter-spacing: 16rpx; margin-bottom: 8rpx; }
    .code-tip { display: block; font-size: 22rpx; color: #999; }
  }
}

.family-list {
  background: #fff; border-radius: 20rpx; padding: 30rpx; margin-top: 20rpx;
  .section-title { display: block; font-size: 30rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; }
  .family-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 20rpx 0; border-bottom: 1rpx solid #f0f0f0;
    &:last-child { border-bottom: none; }
  }
  .member-info { display: flex; align-items: center; gap: 16rpx; }
  .member-avatar { font-size: 48rpx; }
  .member-name { display: block; font-size: 28rpx; font-weight: bold; color: #333; }
  .member-relation { display: block; font-size: 22rpx; color: #999; }
  .member-actions { display: flex; gap: 16rpx; }
  .view-btn { font-size: 24rpx; color: #4a90e2; padding: 8rpx 16rpx; background: rgba(74,144,226,0.1); border-radius: 16rpx; }
  .unbind-btn { font-size: 24rpx; color: #ff4d4f; padding: 8rpx 16rpx; }
}

.empty-tip { text-align: center; padding: 60rpx; color: #ccc; font-size: 28rpx; margin-top: 40rpx; }

.bind-modal {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 9999;
  .modal-content {
    background: #fff; border-radius: 24rpx; padding: 40rpx; width: 600rpx;
    .modal-title { display: block; font-size: 34rpx; font-weight: bold; text-align: center; margin-bottom: 30rpx; }
    .code-input {
      width: 100%; height: 88rpx; border: 2rpx solid #e8e8e8; border-radius: 16rpx;
      padding: 0 24rpx; font-size: 36rpx; text-align: center; letter-spacing: 16rpx; margin-bottom: 30rpx;
    }
    .modal-confirm {
      width: 100%; height: 88rpx; background: #4a90e2; color: #fff;
      border-radius: 44rpx; font-size: 30rpx; border: none;
    }
  }
}
</style>
