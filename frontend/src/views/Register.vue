<template>
  <div class="register-page">
    <!-- 主容器 -->
    <div class="register-container">
      <!-- 注册区域 -->
      <div class="register-section">
        <div class="register-card">
          <div class="register-header">
            <h2 class="register-title">注册账号</h2>
            <p class="register-desc">创建账户以使用系统功能</p>
          </div>
          
          <el-form 
            ref="registerFormRef" 
            :model="registerForm" 
            :rules="rules"
            class="register-form"
          >
            <div class="form-group">
              <label class="form-label">用户名</label>
              <el-input
                v-model="registerForm.username"
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
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                class="form-input"
                prefix-icon="Lock"
                size="large"
                show-password
                clearable
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">确认密码</label>
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                class="form-input"
                prefix-icon="Lock"
                size="large"
                show-password
                clearable
              />
            </div>
            
            <div class="form-actions">
              <el-button 
                type="primary" 
                @click="handleRegister" 
                :loading="loading"
                class="register-btn"
                size="large"
              >
                注 册
              </el-button>
              
              <div class="form-links">
                <router-link to="/login" class="login-link">
                  已有账号？立即登录
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
const registerFormRef = ref(null)
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})
const loading = ref(false)

// 自定义验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    await axios.post('/api/user/register', {
      username: registerForm.value.username,
      password: registerForm.value.password
    })
    
    ElMessage.success('注册成功，正在跳转到登录页面...')
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    console.error('注册错误:', err)
    if (err.response?.data?.detail) {
      ElMessage.error(err.response.data.detail)
    } else if (err.message) {
      ElMessage.error(err.message)
    } else {
      ElMessage.error('注册失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 400px;
}

.register-section {
  width: 100%;
}

.register-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 40px;
  border: 1px solid #e9ecef;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.register-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.register-form {
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

.register-btn {
  width: 100%;
  height: 44px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  background: #2c3e50;
  border: none;
  transition: all 0.3s ease;
}

.register-btn:hover:not(:disabled) {
  background: #34495e;
}

.register-btn:disabled {
  opacity: 0.7;
}

.form-links {
  text-align: center;
}

.login-link {
  color: #2c3e50;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
}

.login-link:hover {
  color: #1a252f;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-card {
    padding: 24px;
  }
  
  .register-title {
    font-size: 20px;
  }
  
  .form-input {
    height: 40px;
  }
}
</style>