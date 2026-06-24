<template>
  <div class="user-manage-container">
    <div class="page-header">
      <div class="header-info">
        <h1 class="page-title">👥 用户管理</h1>
        <p class="page-subtitle">管理系统用户账户</p>
      </div>
      <el-button type="primary" @click="showAddUserDialog = true" class="add-btn">
        <span class="btn-icon">➕</span>
        <span class="btn-text">添加用户</span>
      </el-button>
    </div>
    
    <el-card class="main-card">
      <div class="table-wrapper">
        <el-table :data="users" border class="user-table">
          <el-table-column prop="id" label="ID" width="80" align="center">
            <template #default="scope">
              <span class="id-badge">{{ scope.row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="用户名">
            <template #default="scope">
              <div class="user-info">
                <span class="user-icon">👤</span>
                <span class="username">{{ scope.row.username }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" align="center">
            <template #default="scope">
              <div class="action-buttons">
                <el-button size="small" @click="editUser(scope.row)" class="action-btn edit-btn">
                  <span>🔄</span>
                  <span>修改密码</span>
                </el-button>
                <el-button size="small" type="danger" @click="deleteUser(scope.row.id)" class="action-btn delete-btn">
                  <span>🗑️</span>
                  <span>删除</span>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="users.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p class="empty-text">暂无用户数据</p>
          <el-button type="primary" @click="showAddUserDialog = true">添加第一个用户</el-button>
        </div>
      </div>
    </el-card>

    <el-dialog 
      title="添加用户" 
      v-model="showAddUserDialog" 
      width="450px"
      class="custom-dialog"
    >
      <el-form :model="addUserForm" class="dialog-form">
        <el-form-item label="用户名" class="form-item">
          <el-input 
            v-model="addUserForm.username" 
            placeholder="请输入用户名"
            class="form-input"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="密码" class="form-item">
          <el-input 
            v-model="addUserForm.password" 
            type="password" 
            placeholder="请输入密码（至少6位）"
            class="form-input"
            prefix-icon="Lock"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddUserDialog = false" class="dialog-btn cancel-btn">取消</el-button>
        <el-button type="primary" @click="addUser" class="dialog-btn confirm-btn">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog 
      title="修改密码" 
      v-model="showEditDialog" 
      width="450px"
      class="custom-dialog"
    >
      <el-form :model="editForm" class="dialog-form">
        <el-form-item label="原密码" class="form-item">
          <el-input 
            v-model="editForm.old_password" 
            type="password" 
            placeholder="请输入原密码"
            class="form-input"
            prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item label="新密码" class="form-item">
          <el-input 
            v-model="editForm.new_password" 
            type="password" 
            placeholder="请输入新密码（至少6位）"
            class="form-input"
            prefix-icon="Lock"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false" class="dialog-btn cancel-btn">取消</el-button>
        <el-button type="primary" @click="changePassword" class="dialog-btn confirm-btn">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const users = ref([])
const showAddUserDialog = ref(false)
const showEditDialog = ref(false)
const editingUserId = ref(null)

const addUserForm = ref({
  username: '',
  password: ''
})

const editForm = ref({
  old_password: '',
  new_password: ''
})

const loadUsers = async () => {
  try {
    const res = await axios.get('/api/user/list')
    users.value = res.data
  } catch (err) {
    ElMessage.error('获取用户列表失败')
  }
}

const addUser = async () => {
  if (!addUserForm.value.username || !addUserForm.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  
  if (addUserForm.value.password.length < 6) {
    ElMessage.warning('密码至少需要6位')
    return
  }
  
  try {
    await axios.post('/api/user/register', addUserForm.value)
    ElMessage.success('添加成功')
    showAddUserDialog.value = false
    addUserForm.value = { username: '', password: '' }
    await loadUsers()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '添加失败')
  }
}

const editUser = (user) => {
  editingUserId.value = user.id
  editForm.value = { old_password: '', new_password: '' }
  showEditDialog.value = true
}

const changePassword = async () => {
  if (!editForm.value.old_password || !editForm.value.new_password) {
    ElMessage.warning('请填写原密码和新密码')
    return
  }
  
  if (editForm.value.new_password.length < 6) {
    ElMessage.warning('新密码至少需要6位')
    return
  }
  
  try {
    await axios.put(`/api/user/${editingUserId.value}/password`, editForm.value)
    ElMessage.success('修改成功')
    showEditDialog.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '修改失败')
  }
}

const deleteUser = async (userId) => {
  if (!confirm('确定要删除该用户吗？')) {
    return
  }
  
  try {
    await axios.delete(`/api/user/${userId}`)
    ElMessage.success('删除成功')
    await loadUsers()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-manage-container {
  padding: 24px;
  min-height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(102,126,234,0.3);
}

.header-info {
  color: #fff;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255,255,255,0.8);
  margin: 0;
}

.add-btn {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px;
  font-weight: 600;
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  transition: all 0.3s ease;
}

.add-btn:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-2px);
}

.btn-icon {
  margin-right: 6px;
}

.main-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: none;
}

.table-wrapper {
  padding: 10px;
}

.user-table {
  border-radius: 12px;
  overflow: hidden;
}

.user-table thead {
  background: #f8f9fa;
}

.user-table th {
  font-weight: 600;
  color: #666;
}

.id-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-icon {
  font-size: 20px;
}

.username {
  font-weight: 500;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.edit-btn {
  background: #f0f9ff;
  border-color: #7dd3fc;
  color: #0ea5e9;
}

.edit-btn:hover {
  background: #e0f2fe;
  transform: translateY(-1px);
}

.delete-btn {
  background: #fef2f2;
  border-color: #fca5a5;
  color: #ef4444;
}

.delete-btn:hover {
  background: #fee2e2;
  transform: translateY(-1px);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  color: #999;
  margin-bottom: 20px;
}

.custom-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.dialog-form {
  padding: 20px 0;
}

.form-item {
  margin-bottom: 20px;
}

.form-input {
  height: 44px;
  border-radius: 10px;
  font-size: 14px;
}

.dialog-btn {
  padding: 0 24px;
  height: 40px;
  border-radius: 10px;
  font-weight: 500;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: none;
}

.cancel-btn:hover {
  background: #e8e8e8;
}

.confirm-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.confirm-btn:hover {
  transform: translateY(-1px);
}
</style>