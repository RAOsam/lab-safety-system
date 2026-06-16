<template>
  <div>
    <el-card>
      <template #header><span style="font-weight: bold; font-size: 18px;">📷 图像隐患识别</span></template>
      <el-upload
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept="image/*"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽或点击上传实验室现场照片</div>
      </el-upload>
      <div style="margin-top: 16px;">
        <el-button type="primary" @click="uploadImage" :loading="loading">开始识别</el-button>
      </div>
    </el-card>

    <el-card v-if="result" style="margin-top: 20px;">
      <template #header>识别结果</template>
      <div v-if="!result.has_hazard" style="color: #67c23a; font-size: 16px;">✅ 未发现明显安全隐患</div>
      <div v-else>
        <div v-for="(item, idx) in result.suggestions" :key="idx" style="margin-bottom: 16px;">
          <el-alert :title="item.hazard" type="warning" show-icon />
          <div style="margin-top: 8px; background: #f5f5f5; padding: 10px; border-radius: 6px;" v-html="item.advice.replace(/\n/g, '<br>')"></div>
        </div>
        <el-divider>检测到的物体</el-divider>
        <div>{{ result.detections.map(d => `${d.class}(${(d.confidence*100).toFixed(1)}%)`).join('、') }}</div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { UploadFilled } from '@element-plus/icons-vue'

const file = ref(null)
const loading = ref(false)
const result = ref(null)

const handleFileChange = (uploadFile) => {
  file.value = uploadFile.raw
}

const uploadImage = async () => {
  if (!file.value) {
    ElMessage.warning('请先上传图片')
    return
  }
  loading.value = true
  const formData = new FormData()
  formData.append('file', file.value)
  try {
    const res = await axios.post('/api/image/inspect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    result.value = res.data
  } catch (err) {
    console.error(err)
    ElMessage.error('识别失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.el-upload { width: 100%; }
</style>