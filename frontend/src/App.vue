<template>
  <div id="app">
    <header class="main-header">
      <div class="header-content">
        <div class="logo-section">
          <span class="logo-icon">🔬</span>
          <span class="logo-text">实验室安全系统</span>
        </div>
        
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <span class="nav-icon">💬</span>
            <span class="nav-text">问答咨询</span>
          </router-link>
          <router-link to="/image" class="nav-item" :class="{ active: $route.path === '/image' }">
            <span class="nav-icon">🖼️</span>
            <span class="nav-text">图像识别</span>
          </router-link>
          <router-link to="/inspection" class="nav-item" :class="{ active: $route.path === '/inspection' }">
            <span class="nav-icon">📋</span>
            <span class="nav-text">检查记录</span>
          </router-link>
          <router-link to="/users" class="nav-item" v-if="currentUser" :class="{ active: $route.path === '/users' }">
            <span class="nav-icon">👥</span>
            <span class="nav-text">用户管理</span>
          </router-link>
        </nav>
        
        <div class="user-section" v-if="currentUser">
          <div class="user-info">
            <span class="user-avatar">👤</span>
            <span class="user-name">{{ currentUser.username }}</span>
          </div>
          <button @click="handleLogout" class="logout-btn">
            <span class="logout-icon">🚪</span>
            <span class="logout-text">退出</span>
          </button>
        </div>
        <router-link to="/login" class="login-link" v-else>
          <span class="login-icon">🔐</span>
          <span class="login-text">登录</span>
        </router-link>
      </div>
    </header>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="main-footer">
      <p class="footer-text">© 2026 实验室安全智能问答系统</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const currentUser = ref(null)

const loadUser = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
    } catch (e) {
      localStorage.removeItem('user')
      currentUser.value = null
    }
  } else {
    currentUser.value = null
  }
}

provide('loadUser', loadUser)

const handleLogout = () => {
  localStorage.removeItem('user')
  currentUser.value = null
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(loadUser)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f0f2f5;
  min-height: 100vh;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 20px rgba(102,126,234,0.3);
  padding: 0 30px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.nav-menu {
  display: flex;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 25px;
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-item:hover {
  background: rgba(255,255,255,0.15);
  color: #fff;
}

.nav-item.active {
  background: rgba(255,255,255,0.25);
  color: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
}

.nav-icon {
  font-size: 16px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 15px;
  background: rgba(255,255,255,0.15);
  border-radius: 25px;
}

.user-avatar {
  font-size: 18px;
}

.user-name {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(239,68,68,0.9);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(239,68,68,1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239,68,68,0.4);
}

.logout-icon {
  font-size: 14px;
}

.login-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: rgba(255,255,255,0.2);
  border-radius: 25px;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-link:hover {
  background: rgba(255,255,255,0.3);
}

.login-icon {
  font-size: 14px;
}

.main-content {
  flex: 1;
  padding: 20px;
}

.main-footer {
  background: #fff;
  padding: 20px;
  text-align: center;
  border-top: 1px solid #e8e8e8;
}

.footer-text {
  color: #999;
  font-size: 14px;
}
</style>