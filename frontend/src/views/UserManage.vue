<template>
  <div class="user-manage-container">
    <div class="user-manage-content">
      <div class="manage-header">
        <h1 class="manage-title">用户管理</h1>
        <p class="manage-desc">管理系统用户</p>
      </div>

      <div class="main-layout">
        <!-- 左侧表单区域 -->
        <div class="form-section">
          <div class="form-card">
            <h2 class="form-title">{{ editingUser ? '编辑用户' : '添加用户' }}</h2>
            <el-form 
              ref="userFormRef" 
              :model="userForm" 
              :rules="rules"
              label-width="100px"
              class="user-form"
            >
              <el-form-item label="用户名" prop="username">
                <el-input
                  v-model="userForm.username"
                  placeholder="请输入用户名"
                  :disabled="editingUser !== null"
                />
              </el-form-item>

              <el-form-item label="密码" prop="password" v-if="!editingUser">
                <el-input
                  v-model="userForm.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                />
              </el-form-item>

              <el-form-item label="邮箱" prop="email">
                <el-input
                  v-model="userForm.email"
                  placeholder="请输入邮箱"
                />
              </el-form-item>

              <el-form-item label="手机号" prop="phone">
                <el-input
                  v-model="userForm.phone"
                  placeholder="请输入手机号"
                />
              </el-form-item>

              <el-form-item label="部门" prop="department">
                <el-input
                  v-model="userForm.department"
                  placeholder="请输入部门"
                />
              </el-form-item>

              <el-form-item label="角色" prop="role">
                <el-select
                  v-model="userForm.role"
                  placeholder="请选择角色"
                  style="width: 100%"
                >
                  <el-option label="管理员" value="admin" />
                  <el-option label="用户" value="user" />
                </el-select>
              </el-form-item>

              <el-form-item>
                <div class="form-actions">
                  <el-button 
                    type="primary" 
                    @click="submitUser" 
                    :loading="submitting"
                    style="flex: 1"
                  >
                    {{ editingUser ? '更新' : '添加' }}
                  </el-button>
                  <el-button 
                    @click="resetForm" 
                    v-if="editingUser !== null"
                    style="flex: 1"
                  >
                    取消
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 右侧列表区域 -->
        <div class="list-section">
          <div class="list-card">
            <div class="list-header">
              <h2 class="list-title">用户列表</h2>
              <div class="stats-info">
                <span class="stat-item">总数: {{ users.length }}</span>
                <span class="stat-item">管理员: {{ adminCount }}</span>
                <span class="stat-item">用户: {{ userCount }}</span>
              </div>
            </div>

            <div class="users-list">
              <div v-if="loadingList" class="loading-state">
                <p>加载中...</p>
              </div>
              <div v-else-if="users.length === 0" class="empty-state">
                <p>暂无用户</p>
              </div>
              <div v-else class="list-content">
                <div 
                  v-for="user in users" 
                  :key="user.id" 
                  class="user-item"
                  :class="getRoleClass(user.role)"
                >
                  <div class="user-header">
                    <div class="user-avatar">
                      {{ user.username.charAt(0).toUpperCase() }}
                    </div>
                    <div class="user-info">
                      <span class="user-name">{{ user.username }}</span>
                      <span class="user-role">{{ getRoleText(user.role) }}</span>
                    </div>
                  </div>
                  
                  <div class="user-details">
                    <div class="detail-item" v-if="user.email">
                      邮箱: {{ user.email }}
                    </div>
                    <div class="detail-item" v-if="user.phone">
                      手机: {{ user.phone }}
                    </div>
                    <div class="detail-item" v-if="user.department">
                      部门: {{ user.department }}
                    </div>
                  </div>

                  <div class="user-actions">
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="handleEdit(user)"
                    >
                      编辑
                    </el-button>
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="handleDelete(user)"
                      :disabled="user.username === currentUser?.username"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const userFormRef = ref(null)
const userForm = ref({
  username: '',
  password: '',
  email: '',
  phone: '',
  department: '',
  role: 'user'
})
const editingUser = ref(null)
const submitting = ref(false)
const loadingList = ref(false)
const users = ref([])

const currentUser = ref(null)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const adminCount = computed(() => 
  users.value.filter(user => user.role === 'admin').length
)

const userCount = computed(() => 
  users.value.filter(user => user.role === 'user').length
)

const loadCurrentUser = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
    } catch (e) {
      currentUser.value = null
    }
  }
}

const loadUsers = async () => {
  loadingList.value = true
  try {
    const res = await axios.get('/api/users')
    users.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败，请重试')
  } finally {
    loadingList.value = false
  }
}

const submitUser = async () => {
  if (!userFormRef.value) return

  try {
    await userFormRef.value.validate()
    submitting.value = true

    if (editingUser.value) {
      // 更新用户
      await axios.put(`/api/users/${editingUser.value.id}`, {
        email: userForm.value.email,
        phone: userForm.value.phone,
        department: userForm.value.department,
        role: userForm.value.role
      })
      
      const index = users.value.findIndex(u => u.id === editingUser.value.id)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...userForm.value }
      }
      
      ElMessage.success('更新成功')
    } else {
      // 添加用户
      const res = await axios.post('/api/users', {
        username: userForm.value.username,
        password: userForm.value.password,
        email: userForm.value.email,
        phone: userForm.value.phone,
        department: userForm.value.department,
        role: userForm.value.role
      })
      
      users.value.unshift(res.data)
      ElMessage.success('添加成功')
    }
    
    resetForm()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    submitting.value = false
  }
}

const handleEdit = (user) => {
  editingUser.value = user
  userForm.value = {
    username: user.username,
    password: '',
    email: user.email || '',
    phone: user.phone || '',
    department: user.department || '',
    role: user.role
  }
}

const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm('确认删除此用户？', '警告', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/users/${user.id}`)
    
    users.value = users.value.filter(u => u.id !== user.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const resetForm = () => {
  editingUser.value = null
  userForm.value = {
    username: '',
    password: '',
    email: '',
    phone: '',
    department: '',
    role: 'user'
  }
  if (userFormRef.value) {
    userFormRef.value.clearValidate()
  }
}

const getRoleText = (role) => {
  const map = {
    admin: '管理员',
    user: '用户'
  }
  return map[role] || role
}

const getRoleClass = (role) => {
  return `role-${role}`
}

onMounted(() => {
  loadCurrentUser()
  loadUsers()
})
</script>

<style scoped>
.user-manage-container {
  min-height: calc(100vh - 140px);
  background: #f5f7fa;
  padding: 20px;
}

.user-manage-content {
  max-width: 1400px;
  margin: 0 auto;
}

.manage-header {
  margin-bottom: 24px;
}

.manage-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.manage-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.main-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-section {
  display: flex;
  flex-direction: column;
}

.form-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  padding: 24px;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.user-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-actions {
  display: flex;
  gap: 8px;
  width: 100%;
}

.list-section {
  display: flex;
  flex-direction: column;
}

.list-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  padding: 24px;
  max-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.list-header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.list-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
}

.stats-info {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #666;
}

.stat-item {
  padding: 4px 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.users-list {
  flex: 1;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.list-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-item {
  background: #f5f7fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  transition: all 0.3s ease;
}

.user-item:hover {
  border-color: #2c3e50;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: #2c3e50;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.role-admin .user-avatar {
  background: #2c3e50;
}

.role-user .user-avatar {
  background: #667eea;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.user-role {
  font-size: 12px;
  color: #666;
}

.user-details {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item {
  font-size: 12px;
  color: #666;
}

.user-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .list-card {
    max-height: 500px;
  }
}

@media (max-width: 768px) {
  .user-manage-container {
    padding: 10px;
  }
  
  .manage-title {
    font-size: 20px;
  }
  
  .form-card,
  .list-card {
    padding: 16px;
  }
  
  .user-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>