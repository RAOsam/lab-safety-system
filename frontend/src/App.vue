<template>
  <div id="app">
    <!-- 左侧栏 -->
    <aside class="sidebar">
      <!-- Logo -->
      <div class="sidebar-header">
        <router-link to="/" class="sidebar-logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7V12C2 16.5 4.23 20.68 7.62 23L12 24L16.38 23C19.77 20.68 22 16.5 22 12V7L12 2Z" fill="currentColor"/>
            </svg>
          </div>
          <span class="logo-text">实验室安全系统</span>
        </router-link>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <div class="nav-section-title">核心功能</div>
        
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <el-icon :size="18"><ChatLineSquare /></el-icon>
          <span class="nav-label">安全问答</span>
        </router-link>
        
        <router-link to="/image" class="nav-item" :class="{ active: $route.path === '/image' }">
          <el-icon :size="18"><Camera /></el-icon>
          <span class="nav-label">图像识别</span>
        </router-link>
        
        <router-link to="/inspection" class="nav-item" :class="{ active: $route.path === '/inspection' }">
          <el-icon :size="18"><DocumentChecked /></el-icon>
          <span class="nav-label">检查管理</span>
        </router-link>

        <div class="nav-section-title" v-if="currentUser">系统管理</div>
        
        <router-link to="/users" class="nav-item" v-if="currentUser" :class="{ active: $route.path === '/users' }">
          <el-icon :size="18"><UserFilled /></el-icon>
          <span class="nav-label">用户管理</span>
        </router-link>
      </nav>

      <!-- 底部用户区域 -->
      <div class="sidebar-footer">
        <div v-if="currentUser" class="user-card">
          <div class="user-avatar">{{ currentUser.username.charAt(0).toUpperCase() }}</div>
          <div class="user-meta">
            <span class="user-name">{{ currentUser.username }}</span>
            <span class="user-role">{{ currentUser.role === 'admin' ? '管理员' : '用户' }}</span>
          </div>
          <button @click="handleLogout" class="logout-btn" title="退出登录">
            <el-icon :size="16"><SwitchButton /></el-icon>
          </button>
        </div>
        <router-link to="/login" class="login-card" v-else>
          <el-icon :size="18"><User /></el-icon>
          <span>登录</span>
        </router-link>
      </div>
    </aside>

    <!-- 右侧主区域 -->
    <div class="main-area">
      <!-- 顶部栏 -->
      <header class="top-bar">
        <div class="page-title">
          <span v-if="$route.path === '/'">安全问答</span>
          <span v-else-if="$route.path === '/image'">图像识别</span>
          <span v-else-if="$route.path === '/inspection'">检查管理</span>
          <span v-else-if="$route.path === '/users'">用户管理</span>
          <span v-else-if="$route.path === '/login'">登录</span>
          <span v-else-if="$route.path === '/register'">注册</span>
          <span v-else>实验室安全系统</span>
        </div>
        <div class="top-bar-right">
          <span class="top-bar-desc">安全第一，预防为主</span>
        </div>
      </header>

      <!-- 内容区域 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const currentUser = ref(null)

const loadUser = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
      const token = localStorage.getItem('access_token')
      if (token) {
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + token
      }
    } catch (e) {
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      currentUser.value = null
    }
  } else {
    currentUser.value = null
  }
}

provide('loadUser', loadUser)

const handleLogout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('access_token')
  delete axios.defaults.headers.common['Authorization']
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  background: #f0f2f5;
  min-height: 100vh;
  color: #2c3e50;
}

#app {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ===== 左侧栏 ===== */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #1a1a2e;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px 16px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4c6ef5;
  border-radius: 8px;
  color: #fff;
  padding: 6px;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

/* 导航菜单 */
.sidebar-nav {
  flex: 1;
  padding: 12px 12px;
  overflow-y: auto;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.35);
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 16px 12px 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin: 2px 0;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.9);
}

.nav-item.active {
  background: rgba(76, 110, 245, 0.2);
  color: #fff;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: #4c6ef5;
  border-radius: 0 3px 3px 0;
}

.nav-label {
  white-space: nowrap;
}

/* 底部用户区域 */
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
}

.user-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4c6ef5;
  border-radius: 50%;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.user-name {
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.3;
}

.user-role {
  color: rgba(255, 255, 255, 0.45);
  font-size: 11px;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.login-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.65);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.login-card:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

/* ===== 右侧主区域 ===== */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部栏 */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.top-bar-right {
  display: flex;
  align-items: center;
}

.top-bar-desc {
  font-size: 13px;
  color: #999;
}

/* 内容区域 */
.main-content {
  flex: 1;
  padding: 20px 24px;
  overflow-y: auto;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
    min-width: 60px;
  }

  .sidebar .logo-text,
  .sidebar .nav-label,
  .sidebar .nav-section-title,
  .sidebar .user-meta,
  .sidebar .login-card span {
    display: none;
  }

  .sidebar-logo {
    justify-content: center;
  }

  .nav-item {
    justify-content: center;
    padding: 10px;
  }

  .nav-item.active::before {
    left: -12px;
  }

  .user-card {
    justify-content: center;
    padding: 8px;
  }

  .top-bar {
    padding: 0 16px;
  }

  .main-content {
    padding: 16px;
  }
}
</style>