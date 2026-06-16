<template>
  <div class="chat-container">
    <el-card class="chat-card">
      <template #header>
        <span style="font-weight: bold; font-size: 18px;">💬 实验室安全问答</span>
      </template>
      <div class="chat-box" ref="chatBoxRef">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
          <div class="role-label">{{ msg.role === 'user' ? '👤 我' : '🤖 安全助手' }}</div>
          <div class="content" v-html="formatAnswer(msg.content)"></div>
        </div>
        <div v-if="loading" class="message assistant">
          <div class="role-label">🤖 安全助手</div>
          <div class="content">思考中...</div>
        </div>
      </div>
      <div class="input-area">
        <el-input
          type="textarea"
          v-model="currentQuestion"
          placeholder="描述实验室安全隐患，例如：浓硫酸溅到桌面怎么办？"
          :rows="3"
          resize="none"
          @keydown.ctrl.enter="sendQuestion"
        />
        <el-button type="primary" @click="sendQuestion" :loading="loading" style="margin-top: 10px;">
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const messages = ref([])
const currentQuestion = ref('')
const loading = ref(false)
const chatBoxRef = ref(null)

const formatAnswer = (text) => {
  return text.replace(/\n/g, '<br>')
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatBoxRef.value) {
    chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight
  }
}

const sendQuestion = async () => {
  if (!currentQuestion.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  messages.value.push({ role: 'user', content: currentQuestion.value })
  const question = currentQuestion.value
  currentQuestion.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await axios.post('/api/qa/ask', { question })
    messages.value.push({ role: 'assistant', content: res.data.answer })
  } catch (err) {
    console.error(err)
    messages.value.push({ role: 'assistant', content: '系统出错，请稍后重试。' })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
.chat-container { max-width: 800px; margin: 0 auto; }
.chat-box { height: 450px; overflow-y: auto; padding: 10px; background: #fafafa; border-radius: 8px; border: 1px solid #e4e7ed; }
.message { margin-bottom: 16px; }
.message.user { text-align: right; }
.message.assistant { text-align: left; }
.role-label { font-weight: bold; font-size: 0.9em; color: #666; margin-bottom: 4px; }
.content { display: inline-block; background: #fff; padding: 10px 14px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: left; max-width: 80%; }
.message.user .content { background: #409EFF; color: #fff; }
.input-area { margin-top: 16px; }
</style>