<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <header class="main-header">
      <div class="header-content">
        <div class="logo-section">
          <div class="logo-container">
            <svg class="logo-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7V12C2 16.5 4.23 20.68 7.62 23L12 24L16.38 23C19.77 20.68 22 16.5 22 12V7L12 2Z" fill="white" opacity="0.9"/>
              <path d="M12 2L2 7V12C2 16.5 4.23 20.68 7.62 23L12 24L16.38 23C19.77 20.68 22 16.5 22 12V7L12 2Z" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="12" r="3" fill="white" opacity="0.8"/>
            </svg>
            <span class="logo-text">实验室安全智能系统</span>
          </div>
        </div>
        
        <nav class="nav-menu">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <div class="nav-icon-container">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15C21 16.1 20.1 17 19 17H8L3 21V5C3 3.9 3.9 3 5 3H19C20.1 3 21 3.9 21 5V15Z" fill="currentColor"/>
              </svg>
            </div>
            <span class="nav-text">安全问答</span>
          </router-link>
          <router-link to="/image" class="nav-item" :class="{ active: $route.path === '/image' }">
            <div class="nav-icon-container">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" fill="currentColor"/>
                <circle cx="8.5" cy="8.5" r="1.5" fill="white"/>
                <polyline points="21 15 16 10 5 21" fill="white"/>
              </svg>
            </div>
            <span class="nav-text">图像识别</span>
          </router-link>
          <router-link to="/inspection" class="nav-item" :class="{ active: $route.path === '/inspection' }">
            <div class="nav-icon-container">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 11H15M9 15H13M21 11C21 16.5228 16.5228 21 11 21C5.47715 21 1 16.5228 1 11C1 5.47715 5.47715 1 11 1C16.5228 1 21 5.47715 21 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M11 3V1M11 21V23M3 11H1M21 11H23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span class="nav-text">检查管理</span>
          </router-link>
          <router-link to="/users" class="nav-item" v-if="currentUser" :class="{ active: $route.path === '/users' }">
            <div class="nav-icon-container">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9 19.1 17 18 17H6C4.9 17 4 17.9 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span class="nav-text">用户管理</span>
          </router-link>
        </nav>
        
        <div class="user-section" v-if="currentUser">
          <div class="user-info">
            <div class="user-avatar">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9 19.1 17 18 17H6C4.9 17 4 17.9 4 19V21" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="7" r="4" stroke="white" stroke-width="2"/>
              </svg>
            </div>
            <div class="user-details">
              <span class="user-name">{{ currentUser.username }}</span>
              <span class="user-role">管理员</span>
            </div>
          </div>
          <button @click="handleLogout" class="logout-btn">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 21H5C4.44772 21 4 20.5523 4 20V4C4 3.44772 4.44772 3 5 3H9M16 17L21 12M21 12L16 7M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="logout-text">退出</span>
          </button>
        </div>
        <router-link to="/login" class="login-link" v-else>
          <div class="login-icon-container">
            <svg class="login-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H15M16 17L21 12M21 12L16 7M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="login-text">登录</span>
        </router-link>
      </div>
    </header>
    
    <!-- 主要内容区域 -->
    <main class="main-content">
      <router-view />
    </main>
    
    <!-- 页脚 -->
    <footer class="main-footer">
      <div class="footer-content">
        <div class="footer-info">
          <p class="footer-text">© 2026 实验室安全智能问答系统</p>
          <p class="footer-desc">安全第一，预防为主，综合治理</p>
        </div>
        <div class="footer-links">
          <a href="#" class="footer-link">使用指南</a>
          <a href="#" class="footer-link">安全规范</a>
          <a href="#" class="footer-link">联系我们</a>
        </div>
      </div>
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
  background: #f5f7fa;
  min-height: 100vh;
  color: #2c3e50;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 顶部导航栏样式 */
.main-header {
  background: #2c3e50;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0 30px;
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid #e9ecef;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  max-width: 1400px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.logo-container:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.logo-icon {
  width: 32px;
  height: 32px;
  fill: white;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.nav-item:hover::before {
  left: 100%;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.nav-icon-container {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.nav-text {
  white-space: nowrap;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.15);
}

.user-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-name {
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.user-role {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(239, 68, 68, 0.9);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.logout-icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.login-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-link:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.login-icon-container {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

/* 主要内容区域样式 */
.main-content {
  flex: 1;
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 页脚样式 */
.main-footer {
  background: #1a1a1a;
  padding: 30px 0;
  border-top: 1px solid #333;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-text {
  color: #fff;
  font-size: 14px;
  font-weight: 500;
}

.footer-desc {
  color: #999;
  font-size: 12px;
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-link {
  color: #999;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #fff;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-content {
    flex-wrap: wrap;
    height: auto;
    padding: 15px;
    gap: 15px;
  }
  
  .nav-menu {
    order: 3;
    flex-wrap: wrap;
    width: 100%;
    justify-content: center;
  }
  
  .user-section {
    order: 2;
  }
  
  .logo-section {
    order: 1;
  }
}

@media (max-width: 768px) {
  .main-header {
    padding: 0 15px;
  }
  
  .main-content {
    padding: 20px 15px;
  }
  
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .footer-links {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-item {
    padding: 10px 15px;
    font-size: 13px;
  }
  
  .logo-text {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .nav-menu {
    gap: 4px;
  }
  
  .nav-item {
    padding: 8px 12px;
    gap: 6px;
  }
  
  .nav-text {
    display: none;
  }
  
  .user-name {
    display: none;
  }
  
  .logout-text {
    display: none;
  }
  
  .login-text {
    display: none;
  }
}
</style>