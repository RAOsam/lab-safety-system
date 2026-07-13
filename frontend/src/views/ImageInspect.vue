<template>
  <div class="image-inspect-container">
    <div class="image-inspect-content">
      <div class="inspect-header">
        <h1 class="inspect-title">图像隐患识别</h1>
        <p class="inspect-desc">上传实验室照片，自动识别安全隐患</p>
      </div>

      <div class="main-layout">
        <!-- 左侧上传区域 -->
        <div class="upload-section">
          <div 
            class="upload-area"
            :class="{ 'drag-over': isDragOver }"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
            @click="selectImage"
          >
            <div v-if="!imagePreview" class="upload-placeholder">
              <div class="upload-icon">📷</div>
              <p class="upload-text">点击或拖拽图片到此处</p>
              <p class="upload-hint">支持 JPG、PNG 格式，最大 10MB</p>
            </div>
            <img v-else :src="imagePreview" class="preview-image" alt="上传的图片" />
          </div>

          <div class="upload-actions">
            <el-button 
              type="primary" 
              @click="analyzeImage" 
              :disabled="!imageFile || analyzing"
              :loading="analyzing"
              style="width: 100%"
            >
              开始识别
            </el-button>
            <el-button 
              @click="clearImage" 
              v-if="imageFile"
              style="width: 100%; margin-top: 8px"
            >
              重新上传
            </el-button>
          </div>

          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileChange" 
            accept="image/jpeg,image/png"
            style="display: none"
          />
        </div>

        <!-- 右侧结果区域 -->
        <div class="result-section">
          <div v-if="!analysisResult" class="result-placeholder">
            <p class="placeholder-text">上传图片后点击"开始识别"</p>
          </div>
          <div v-else class="result-content">
            <h2 class="result-title">识别结果</h2>
            
            <div v-if="analysisResult.length > 0" class="dangers-list">
              <div 
                v-for="(item, index) in analysisResult" 
                :key="index" 
                class="danger-item"
              >
                <div class="danger-header">
                  <span class="danger-label">{{ item.class }}</span>
                  <span class="danger-confidence">置信度: {{ (item.confidence * 100).toFixed(1) }}%</span>
                </div>
                <div class="danger-coordinates">
                  位置: X: {{ item.x }}, Y: {{ item.y }}
                </div>
              </div>
            </div>
            <div v-else class="no-danger">
              <p>未检测到明显的安全隐患</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const fileInput = ref(null)
const imageFile = ref(null)
const imagePreview = ref(null)
const isDragOver = ref(false)
const analyzing = ref(false)
const analysisResult = ref(null)

const selectImage = () => {
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files?.[0]
  if (file) {
    processFile(file)
  }
}

const processFile = (file) => {
  if (!file.type.match('image.*')) {
    ElMessage.error('请上传图片文件')
    return
  }
  
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 10MB')
    return
  }

  imageFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  analysisResult.value = null
}

const analyzeImage = async () => {
  if (!imageFile.value) return

  analyzing.value = true
  analysisResult.value = null

  try {
    const formData = new FormData()
    formData.append('image', imageFile.value)

    const res = await axios.post('/api/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    analysisResult.value = res.data.detections
    ElMessage.success('识别完成')
  } catch (error) {
    console.error('识别失败:', error)
    ElMessage.error('识别失败，请重试')
  } finally {
    analyzing.value = false
  }
}

const clearImage = () => {
  imageFile.value = null
  imagePreview.value = null
  analysisResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.image-inspect-container {
  min-height: calc(100vh - 140px);
  background: #f5f7fa;
  padding: 20px;
}

.image-inspect-content {
  max-width: 1200px;
  margin: 0 auto;
}

.inspect-header {
  margin-bottom: 24px;
}

.inspect-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.inspect-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.main-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-area {
  background: #fff;
  border: 2px dashed #e9ecef;
  border-radius: 8px;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.upload-area:hover {
  border-color: #2c3e50;
  background: #f9fafb;
}

.upload-area.drag-over {
  border-color: #2c3e50;
  background: #e8ecf1;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.upload-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.upload-actions {
  display: flex;
  flex-direction: column;
}

.result-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  padding: 24px;
  min-height: 400px;
}

.result-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.placeholder-text {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.result-content {
  height: 100%;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.dangers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 340px;
  overflow-y: auto;
}

.danger-item {
  background: #fff5f5;
  border: 1px solid #ffe0e0;
  border-radius: 4px;
  padding: 12px;
}

.danger-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.danger-label {
  font-weight: 600;
  color: #c53030;
  font-size: 14px;
}

.danger-confidence {
  font-size: 12px;
  color: #666;
}

.danger-coordinates {
  font-size: 12px;
  color: #666;
}

.no-danger {
  text-align: center;
  padding: 40px;
}

.no-danger p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .result-section {
    min-height: 300px;
  }
}

@media (max-width: 768px) {
  .image-inspect-container {
    padding: 10px;
  }
  
  .inspect-title {
    font-size: 20px;
  }
  
  .upload-area {
    min-height: 300px;
  }
  
  .preview-image {
    max-height: 300px;
  }
}
</style>