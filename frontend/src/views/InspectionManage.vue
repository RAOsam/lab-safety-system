<template>
  <div class="inspection-manage-container">
    <div class="inspection-manage-content">
      <div class="manage-header">
        <h1 class="manage-title">检查管理</h1>
        <p class="manage-desc">记录和管理安全隐患检查</p>
      </div>

      <div class="main-layout">
        <!-- 左侧表单区域 -->
        <div class="form-section">
          <div class="form-card">
            <h2 class="form-title">添加检查记录</h2>
            <el-form 
              ref="inspectionFormRef" 
              :model="inspectionForm" 
              :rules="rules"
              label-width="100px"
              class="inspection-form"
            >
              <el-form-item label="隐患描述" prop="description">
                <el-input
                  v-model="inspectionForm.description"
                  placeholder="请描述发现的隐患"
                  type="textarea"
                  :rows="4"
                />
              </el-form-item>

              <el-form-item label="发现地点" prop="location">
                <el-input
                  v-model="inspectionForm.location"
                  placeholder="请输入发现地点"
                />
              </el-form-item>

              <el-form-item label="隐患等级" prop="level">
                <el-select
                  v-model="inspectionForm.level"
                  placeholder="请选择隐患等级"
                  style="width: 100%"
                >
                  <el-option label="低" value="low" />
                  <el-option label="中" value="medium" />
                  <el-option label="高" value="high" />
                </el-select>
              </el-form-item>

              <el-form-item label="发现时间" prop="discovery_time">
                <el-date-picker
                  v-model="inspectionForm.discovery_time"
                  type="datetime"
                  placeholder="选择发现时间"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="负责人" prop="responsible_person">
                <el-input
                  v-model="inspectionForm.responsible_person"
                  placeholder="请输入负责人姓名"
                />
              </el-form-item>

              <el-form-item label="截止日期" prop="deadline">
                <el-date-picker
                  v-model="inspectionForm.deadline"
                  type="date"
                  placeholder="选择整改截止日期"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="submitInspection" 
                  :loading="submitting"
                  style="width: 100%"
                >
                  提交记录
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 右侧列表区域 -->
        <div class="list-section">
          <div class="list-card">
            <div class="list-header">
              <h2 class="list-title">检查记录列表</h2>
              <div class="stats-info">
                <span class="stat-item">总数: {{ inspections.length }}</span>
                <span class="stat-item">待处理: {{ pendingCount }}</span>
                <span class="stat-item">已完成: {{ completedCount }}</span>
              </div>
            </div>

            <div class="inspections-list">
              <div v-if="loadingList" class="loading-state">
                <p>加载中...</p>
              </div>
              <div v-else-if="inspections.length === 0" class="empty-state">
                <p>暂无检查记录</p>
              </div>
              <div v-else class="list-content">
                <div 
                  v-for="item in inspections" 
                  :key="item.id" 
                  class="inspection-item"
                  :class="getLevelClass(item.level)"
                >
                  <div class="item-header">
                    <span class="item-level">{{ getLevelText(item.level) }}</span>
                    <span class="item-status">{{ getStatusText(item.status) }}</span>
                  </div>
                  <div class="item-description">{{ item.description }}</div>
                  <div class="item-info">
                    <span>地点: {{ item.location }}</span>
                    <span>时间: {{ formatDate(item.discovery_time) }}</span>
                  </div>
                  <div class="item-actions">
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="handleComplete(item)"
                      v-if="item.status === 'pending'"
                    >
                      标记完成
                    </el-button>
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="handleDelete(item)"
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

const inspectionFormRef = ref(null)
const inspectionForm = ref({
  description: '',
  location: '',
  level: 'medium',
  discovery_time: new Date(),
  responsible_person: '',
  deadline: null
})
const submitting = ref(false)
const loadingList = ref(false)
const inspections = ref([])

const rules = {
  description: [
    { required: true, message: '请描述发现的隐患', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入发现地点', trigger: 'blur' }
  ],
  level: [
    { required: true, message: '请选择隐患等级', trigger: 'change' }
  ],
  discovery_time: [
    { required: true, message: '请选择发现时间', trigger: 'change' }
  ],
  responsible_person: [
    { required: true, message: '请输入负责人姓名', trigger: 'blur' }
  ],
  deadline: [
    { required: true, message: '请选择整改截止日期', trigger: 'change' }
  ]
}

const pendingCount = computed(() => 
  inspections.value.filter(item => item.status === 'pending').length
)

const completedCount = computed(() => 
  inspections.value.filter(item => item.status === 'completed').length
)

const submitInspection = async () => {
  if (!inspectionFormRef.value) return

  try {
    await inspectionFormRef.value.validate()
    submitting.value = true

    const res = await axios.post('/api/inspections', inspectionForm.value)
    
    inspections.value.unshift(res.data)
    ElMessage.success('添加成功')
    
    // 重置表单
    inspectionForm.value = {
      description: '',
      location: '',
      level: 'medium',
      discovery_time: new Date(),
      responsible_person: '',
      deadline: null
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const loadInspections = async () => {
  loadingList.value = true
  try {
    const res = await axios.get('/api/inspections')
    inspections.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败，请重试')
  } finally {
    loadingList.value = false
  }
}

const handleComplete = async (item) => {
  try {
    await ElMessageBox.confirm('确认标记为已完成？', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'info'
    })

    await axios.put(`/api/inspections/${item.id}`, {
      status: 'completed'
    })

    const index = inspections.value.findIndex(i => i.id === item.id)
    if (index !== -1) {
      inspections.value[index].status = 'completed'
    }
    
    ElMessage.success('已标记为完成')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败，请重试')
    }
  }
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm('确认删除此记录？', '警告', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/inspections/${item.id}`)
    
    inspections.value = inspections.value.filter(i => i.id !== item.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const getLevelText = (level) => {
  const map = {
    low: '低',
    medium: '中',
    high: '高'
  }
  return map[level] || level
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    completed: '已完成'
  }
  return map[status] || status
}

const getLevelClass = (level) => {
  return `level-${level}`
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadInspections()
})
</script>

<style scoped>
.inspection-manage-container {
  min-height: calc(100vh - 140px);
  background: #f5f7fa;
  padding: 20px;
}

.inspection-manage-content {
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

.inspection-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.inspections-list {
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

.inspection-item {
  background: #f5f7fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  transition: all 0.3s ease;
}

.inspection-item:hover {
  border-color: #2c3e50;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.item-level {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.level-low .item-level {
  background: #e8f5e9;
  color: #2e7d32;
}

.level-medium .item-level {
  background: #fff3e0;
  color: #ef6c00;
}

.level-high .item-level {
  background: #ffebee;
  color: #c62828;
}

.item-status {
  font-size: 12px;
  color: #666;
}

.item-description {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.5;
}

.item-info {
  font-size: 12px;
  color: #999;
  margin-bottom: 12px;
  display: flex;
  gap: 16px;
}

.item-actions {
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
  .inspection-manage-container {
    padding: 10px;
  }
  
  .manage-title {
    font-size: 20px;
  }
  
  .form-card,
  .list-card {
    padding: 16px;
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .item-info {
    flex-direction: column;
    gap: 4px;
  }
}
</style>