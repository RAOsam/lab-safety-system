<template>
  <div class="login-page">
    <div class="login-wrapper">
      <div class="login-content">
        <div class="logo-section">
          <div class="logo-icon">🔬</div>
          <h1 class="logo-title">实验室安全系统</h1>
          <p class="logo-subtitle">保障安全，守护科研</p>
        </div>
        
        <el-card class="login-card">
          <template #header>
            <div class="card-header">
              <span class="header-icon">🔐</span>
              <span class="header-title">用户登录</span>
            </div>
          </template>
          
          <el-form :model="loginForm" ref="loginFormRef" class="login-form">
            <el-form-item prop="username" class="form-item">
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名"
                class="input-field"
                prefix-icon="User"
              />
            </el-form-item>
            
            <el-form-item prop="password" class="form-item">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码"
                class="input-field"
                prefix-icon="Lock"
              />
            </el-form-item>
            
            <el-form-item class="form-item">
              <el-button 
                type="primary" 
                @click="handleLogin" 
                :loading="loading" 
                class="login-btn"
              >
                <span class="btn-text">登 录</span>
              </el-button>
            </el-form-item>
            
            <div class="register-link">
              <span>还没有账号？</span>
              <el-link @click="goToRegister" type="primary" class="link-btn">立即注册</el-link>
            </div>
          </el-form>
        </el-card>
      </div>
      
      <div class="login-decoration">
        <div class="deco-circle deco-circle-1"></div>
        <div class="deco-circle deco-circle-2"></div>
        <div class="deco-circle deco-circle-3"></div>
        <div class="deco-shape deco-shape-1"></div>
        <div class="deco-shape deco-shape-2"></div>
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
const loginForm = ref({
  username: '',
  password: ''
})
const loading = ref(false)
const loginFormRef = ref(null)

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const res = await axios.post('/api/user/login', loginForm.value)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    ElMessage.success('登录成功')
    router.push('/')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 900px;
  position: relative;
  z-index: 1;
}

.login-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-section {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.logo-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.logo-subtitle {
  font-size: 16px;
  color: rgba(255,255,255,0.8);
  margin: 0;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
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

.login-form {
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
  border-color: #667eea;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
}

.login-btn {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102,126,234,0.4);
  transition: all 0.3s ease;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102,126,234,0.5);
}

.btn-text {
  letter-spacing: 4px;
}

.register-link {
  text-align: center;
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.link-btn {
  margin-left: 8px;
  font-weight: 500;
}

.login-decoration {
  position: absolute;
  top: 0;
  right: 0;
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
  width: 300px;
  height: 300px;
  background: #fff;
  top: -100px;
  right: -50px;
}

.deco-circle-2 {
  width: 200px;
  height: 200px;
  background: #fff;
  bottom: 50px;
  right: 100px;
}

.deco-circle-3 {
  width: 150px;
  height: 150px;
  background: #fff;
  top: 50%;
  right: -30px;
}

.deco-shape {
  position: absolute;
  background: rgba(255,255,255,0.1);
  border-radius: 20px;
}

.deco-shape-1 {
  width: 100px;
  height: 100px;
  top: 20%;
  right: 150px;
  transform: rotate(45deg);
}

.deco-shape-2 {
  width: 60px;
  height: 60px;
  bottom: 30%;
  right: 50px;
  transform: rotate(15deg);
}
</style>