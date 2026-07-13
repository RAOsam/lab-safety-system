<template>
  <div class="home-container">
    <div class="home-content">
      <!-- 问答区域 -->
      <div class="qa-section">
        <div class="qa-header">
          <h1 class="qa-title">实验室安全问答</h1>
          <p class="qa-desc">请提出您关于实验室安全的问题</p>
        </div>

        <!-- 聊天消息区域 -->
        <div class="chat-container" ref="chatContainer">
          <div class="chat-messages">
            <div 
              v-for="(message, index) in messages" 
              :key="index" 
              class="message-item"
              :class="message.role === 'user' ? 'user-message' : 'ai-message'"
            >
              <div class="message-content">
                {{ message.content }}
              </div>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="loading" class="message-item ai-message">
              <div class="message-content loading">
                正在思考中...
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷问题按钮 -->
        <div class="quick-questions" v-if="messages.length === 0">
          <div class="question-title">常见问题</div>
          <div class="question-buttons">
            <button 
              v-for="question in quickQuestions" 
              :key="question"
              @click="sendQuickQuestion(question)"
              class="question-btn"
            >
              {{ question }}
            </button>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-section">
          <el-input
            v-model="userMessage"
            placeholder="请输入您的问题..."
            class="message-input"
            @keyup.enter="sendMessage"
            :disabled="loading"
            clearable
          >
            <template #append>
              <el-button 
                @click="sendMessage" 
                :disabled="!userMessage.trim() || loading"
                type="primary"
              >
                发送
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const userMessage = ref('')
const messages = ref([])
const loading = ref(false)
const chatContainer = ref(null)

// 快捷问题
const quickQuestions = ref([
  '实验室有哪些基本安全规范？',
  '发生化学品泄漏应该如何处理？',
  '实验室紧急联系电话是什么？',
  '如何正确处理实验废弃物？'
])

const sendMessage = async () => {
  if (!userMessage.value.trim() || loading.value) return

  const message = userMessage.value.trim()
  messages.value.push({
    role: 'user',
    content: message
  })
  
  userMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const res = await axios.post('/api/qa', { question: message })
    
    messages.value.push({
      role: 'assistant',
      content: res.data.answer
    })
    
    scrollToBottom()
  } catch (error) {
    console.error('提问失败:', error)
    ElMessage.error('提问失败，请重试')
    messages.value.pop() // 移除用户消息
  } finally {
    loading.value = false
  }
}

const sendQuickQuestion = (question) => {
  userMessage.value = question
  sendMessage()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      const container = chatContainer.value
      container.scrollTop = container.scrollHeight
    }
  })
}

onMounted(() => {
  // 添加欢迎消息
  messages.value.push({
    role: 'assistant',
    content: '您好！我是实验室安全助手，有什么我可以帮助您的吗？'
  })
})
</script>

<style scoped>
.home-container {
  min-height: calc(100vh - 140px);
  background: #f5f7fa;
  padding: 20px;
}

.home-content {
  max-width: 1000px;
  margin: 0 auto;
}

.qa-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 180px);
}

.qa-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
}

.qa-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.qa-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  margin-bottom: 8px;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
  word-wrap: break-word;
}

.user-message .message-content {
  background: #2c3e50;
  color: #fff;
  border-radius: 8px 8px 0 8px;
}

.ai-message .message-content {
  background: #f5f7fa;
  color: #333;
  border: 1px solid #e9ecef;
  border-radius: 8px 8px 8px 0;
}

.message-content.loading {
  color: #999;
  font-style: italic;
}

.quick-questions {
  padding: 16px 24px;
  border-top: 1px solid #e9ecef;
}

.question-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.question-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.question-btn {
  padding: 8px 16px;
  background: #f5f7fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  color: #2c3e50;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.question-btn:hover {
  background: #e9ecef;
  border-color: #dcdfe6;
}

.input-section {
  padding: 16px 24px;
  border-top: 1px solid #e9ecef;
}

.message-input {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-container {
    padding: 10px;
  }
  
  .qa-section {
    height: calc(100vh - 120px);
  }
  
  .qa-header,
  .chat-container,
  .quick-questions,
  .input-section {
    padding: 16px;
  }
  
  .message-content {
    max-width: 85%;
  }
}

@media (max-width: 480px) {
  .qa-title {
    font-size: 18px;
  }
  
  .question-btn {
    font-size: 13px;
    padding: 6px 12px;
  }
}
</style>