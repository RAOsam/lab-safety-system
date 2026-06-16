<template>
  <div>
    <el-card>
      <template #header><span style="font-weight: bold; font-size: 18px;">📋 新增检查记录</span></template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12"><el-form-item label="位置"><el-input v-model="form.location" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="检查人"><el-input v-model="form.inspector" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="隐患描述"><el-input type="textarea" v-model="form.hazard_description" :rows="2" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="风险等级"><el-select v-model="form.risk_level"><el-option label="高" value="高"/><el-option label="中" value="中"/><el-option label="低" value="低"/></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="责任人"><el-input v-model="form.responsible_person" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="整改期限"><el-date-picker type="date" v-model="form.deadline" value-format="YYYY-MM-DD" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item><el-button type="primary" @click="createRecord">提交</el-button></el-form-item></el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header><span style="font-weight: bold; font-size: 18px;">📋 检查记录列表</span></template>
      <el-table :data="records" stripe style="width: 100%;" max-height="400" :loading="loading">
        <el-table-column prop="location" label="位置" width="120" />
        <el-table-column prop="inspector" label="检查人" width="100" />
        <el-table-column prop="hazard_description" label="隐患描述" show-overflow-tooltip />
        <el-table-column prop="risk_level" label="风险等级" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已整改' ? 'success' : 'danger'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responsible_person" label="责任人" width="80" />
        <el-table-column prop="deadline" label="整改期限" width="150" :formatter="formatDeadline" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
              <el-button size="small" type="success" icon="Check" @click="markCompleted(row.id)" :disabled="row.status === '已整改'">完成</el-button>
              <el-button size="small" type="danger" icon="Delete" @click="deleteRecord(row.id)">删除</el-button>
            </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 表单验证规则
const rules = {
  location: [{ required: true, message: '请填写位置', trigger: 'blur' }],
  inspector: [{ required: true, message: '请填写检查人', trigger: 'blur' }],
  hazard_description: [{ required: true, message: '请填写隐患描述', trigger: 'blur' }],
  risk_level: [{ required: true, message: '请选择风险等级', trigger: 'change' }],
  responsible_person: [{ required: true, message: '请填写责任人', trigger: 'blur' }],
  deadline: [{ required: true, message: '请选择整改期限', trigger: 'change' }]
}

const form = reactive({
  location: '',
  inspector: '',
  hazard_description: '',
  risk_level: '中',
  responsible_person: '',
  deadline: ''
})
const records = ref([])
const loading = ref(false)
const formRef = ref(null)

const fetchRecords = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/inspection/list')
    records.value = res.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (err) {
    console.error(err)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const createRecord = async () => {
  // 表单验证
  await formRef.value.validate()
  
  try {
    await axios.post('/api/inspection/create', form)
    ElMessage.success('添加成功')
    // 重置表单
    formRef.value.resetFields()
    fetchRecords()
  } catch (err) {
    ElMessage.error('添加失败：' + (err.response?.data?.message || err.message))
  }
}

const markCompleted = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要标记为已完成吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.put(`/api/inspection/${id}`, { status: '已整改', completed_at: new Date().toISOString() })
    ElMessage.success('已标记完成')
    fetchRecords()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('操作失败：' + (err.response?.data?.message || err.message))
    }
  }
}

const deleteRecord = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记录吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    await axios.delete(`/api/inspection/${id}`)
    ElMessage.success('删除成功')
    fetchRecords()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败：' + (err.response?.data?.message || err.message))
    }
  }
}

const formatDeadline = (row) => {
  const now = new Date()
  const deadline = new Date(row.deadline)
  
  if (row.status === '已整改') return row.deadline
  
  if (deadline < now) {
    return `<span style='color: #f56c6c; font-weight: bold;'>${row.deadline} (已逾期)</span>`
  } else if (deadline - now < 3 * 24 * 60 * 60 * 1000) {
    return `<span style='color: #e6a23c;'>${row.deadline} (即将到期)</span>`
  }
  return row.deadline
}

onMounted(fetchRecords)
</script>