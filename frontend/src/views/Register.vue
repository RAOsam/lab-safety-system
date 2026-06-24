<template>
  <div class="register-page">
    <div class="register-wrapper">
      <div class="register-decoration">
        <div class="deco-circle deco-circle-1"></div>
        <div class="deco-circle deco-circle-2"></div>
        <div class="deco-circle deco-circle-3"></div>
        <div class="deco-wave deco-wave-1"></div>
        <div class="deco-wave deco-wave-2"></div>
      </div>
      
      <div class="register-content">
        <el-card class="register-card">
          <template #header>
            <div class="card-header">
              <span class="header-icon">📝</span>
              <span class="header-title">用户注册</span>
            </div>
          </template>
          
          <el-form :model="registerForm" ref="registerFormRef" class="register-form">
            <el-form-item prop="username" class="form-item">
              <el-input 
                v-model="registerForm.username" 
                placeholder="请输入用户名"
                class="input-field"
                prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="password" class="form-item">
              <el-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="请输入密码（至少6位）"
                class="input-field"
                prefix-icon="Lock"
              />
            </el-form-item>
            
            <el-form-item prop="confirmPassword" class="form-item">
              <el-input 
                v-model="registerForm.confirmPassword" 
                type="password" 
                placeholder="请再次输入密码"
                class="input-field"
                prefix-icon="Lock"
              />
            </el-form-item>
            
            <el-form-item class="form-item">
              <el-button 
                type="primary" 
                @click="handleRegister" 
                :loading="loading" 
                class="register-btn"
              >
                <span class="btn-text">注 册</span>
              </el-button>
            </el-form-item>
            
            <div class="login-link">
              <span>已有账号？</span>
              <el-link @click="goToLogin" type="primary" class="link-btn">立即登录</el-link>
            </div>
          </el-form>
        </el-card>
        
        <div class="features-section">
          <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">安全可靠</div>
            <div class="feature-desc">密码加密存储</div>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">快速便捷</div>
            <div class="feature-desc">一键注册登录</div>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">隐私保护</div>
            <div class="feature-desc">数据严格保密</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)
const registerFormRef = ref(null)

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  
  if (registerForm.value.password.length < 6) {
    ElMessage.warning('密码至少需要6位')
    return
  }
  
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  loading.value = true
  try {
    await axios.post('/api/user/register', {
      username: registerForm.value.username,
      password: registerForm.value.password
    })
    ElMessage.success('注册成功')
    router.push('/login')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.register-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 900px;
  position: relative;
  z-index: 1;
}

.register-decoration {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 50%;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
}

.deco-circle-1 {
  width: 280px;
  height: 280px;
  background: #fff;
  top: -80px;
  left: -40px;
}

.deco-circle-2 {
  width: 180px;
  height: 180px;
  background: #fff;
  bottom: 30px;
  left: 80px;
}

.deco-circle-3 {
  width: 120px;
  height: 120px;
  background: #fff;
  top: 55%;
  left: -20px;
}

.deco-wave {
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  border: 3px solid rgba(255,255,255,0.1);
}

.deco-wave-1 {
  top: 20%;
  left: 100px;
}

.deco-wave-2 {
  bottom: 25%;
  left: 50px;
  width: 150px;
  height: 150px;
}

.register-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.register-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  border: none;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 24px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.register-form {
  padding: 20px 0;
}

.form-item {
  margin-bottom: 20px;
}

.input-field {
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  transition: all 0.3s ease;
}

.input-field:focus {
  border-color: #11998e;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(17,153,142,0.1);
}

.register-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(17,153,142,0.4);
  transition: all 0.3s ease;
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(17,153,142,0.5);
}

.btn-text {
  letter-spacing: 4px;
}

.login-link {
  text-align: center;
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.link-btn {
  margin-left: 8px;
  font-weight: 500;
}

.features-section {
  display: flex;
  gap: 20px;
  margin-top: 30px;
}

.feature-card {
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  min-width: 100px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255,255,255,0.3);
}

.feature-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 12px;
  color: rgba(255,255,255,0.8);
}
</style>