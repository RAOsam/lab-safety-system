<template>
  <div class="login-page">
    <!-- 主容器 -->
    <div class="login-container">
      <!-- 登录区域 -->
      <div class="login-section">
        <div class="login-card">
          <div class="login-header">
            <h2 class="login-title">安全登录</h2>
            <p class="login-desc">请使用您的账户信息登录系统</p>
          </div>
          
          <el-form 
            ref="loginFormRef" 
            :model="loginForm" 
            :rules="rules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <div class="form-group">
              <label class="form-label">用户名</label>
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                class="form-input"
                prefix-icon="User"
                size="large"
                clearable
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">密码</label>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                class="form-input"
                prefix-icon="Lock"
                size="large"
                show-password
                clearable
                @keyup.enter="handleLogin"
              />
            </div>
            
            <div class="form-actions">
              <el-button 
                type="primary" 
                @click="handleLogin" 
                :loading="loading"
                class="login-btn"
                size="large"
              >
                登 录
              </el-button>
              
              <div class="form-links">
                <router-link to="/register" class="register-link">
                  还没有账号？立即注册
                </router-link>
              </div>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loginFormRef = ref(null)
const loginForm = ref({
  username: '',
  password: ''
})
const loading = ref(false)

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    const res = await axios.post('/api/user/login', loginForm.value)
    
    // 保存JWT token和用户信息
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    
    // 设置axios默认headers
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
    
    ElMessage.success('登录成功，正在跳转...')
    router.push('/')
  } catch (err) {
    console.error('登录错误:', err)
    if (err.response?.data?.detail) {
      ElMessage.error(err.response.data.detail)
    } else if (err.message) {
      ElMessage.error(err.message)
    } else {
      ElMessage.error('登录失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-section {
  width: 100%;
}

.login-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 40px;
  border: 1px solid #e9ecef;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.login-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.form-input {
  height: 44px;
  border-radius: 4px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  background: #fff;
  transition: all 0.3s ease;
}

.form-input:focus {
  border-color: #2c3e50;
  background: #fff;
}

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-btn {
  width: 100%;
  height: 44px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  background: #2c3e50;
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover:not(:disabled) {
  background: #34495e;
}

.login-btn:disabled {
  opacity: 0.7;
}

.form-links {
  text-align: center;
}

.register-link {
  color: #2c3e50;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
}

.register-link:hover {
  color: #1a252f;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 24px;
  }
  
  .login-title {
    font-size: 20px;
  }
  
  .form-input {
    height: 40px;
  }
}
</style>