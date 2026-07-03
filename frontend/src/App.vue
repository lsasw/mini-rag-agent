<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  ChatDotRound,
  Clock,
  Collection,
  Delete,
  DocumentAdd,
  Edit,
  Files,
  Monitor,
  Promotion,
  Search,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import {
  deleteDocument,
  createLlamaDocument,
  deleteLlamaDocument,
  listDocuments,
  listLlamaCategories,
  listLlamaDocuments,
  searchLlamaDocuments,
  sendMessage,
  updateLlamaDocument,
  uploadDocument,
  type DocumentInfo,
  type LlamaDocument,
  type LlamaSearchHit,
  type Source,
} from './api'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  mode?: string
  sources?: Source[]
}

const documents = ref<DocumentInfo[]>([])
const messages = ref<ChatMessage[]>([
  {
    role: 'assistant',
    content:
      '你好，我是 Mini RAG Agent。先上传一份 txt、md 或 pdf，再问我文档里的问题。没有模型 key 时，我会用 mock 回答帮你跑通联调。',
    mode: 'guide',
  },
])
const input = ref('')
const useAgent = ref(false)
const loading = ref(false)
const uploading = ref(false)
const llamaDocuments = ref<LlamaDocument[]>([])
const llamaCategories = ref<string[]>([])
const llamaHits = ref<LlamaSearchHit[]>([])
const selectedCategory = ref('')
const llamaQuery = ref('RAG')
const llamaForm = ref({
  id: '',
  title: 'RAG 核心流程',
  category: 'rag',
  content: 'RAG 包括加载文档、切分文本、检索相关片段、构造 prompt，并调用大模型生成答案。',
})
const llamaSaving = ref(false)

async function refreshDocuments() {
  documents.value = await listDocuments()
}

async function refreshLlama() {
  const [docs, categories] = await Promise.all([
    listLlamaDocuments(selectedCategory.value || undefined),
    listLlamaCategories(),
  ])
  llamaDocuments.value = docs
  llamaCategories.value = categories
}

async function handleUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  uploading.value = true
  try {
    const result = await uploadDocument(file)
    await refreshDocuments()
    ElMessage.success(result.message)
  } catch {
    ElMessage.error('上传失败，请确认后端已启动且文件格式正确')
  } finally {
    uploading.value = false
    target.value = ''
  }
}

async function handleDelete(documentId: string) {
  await deleteDocument(documentId)
  await refreshDocuments()
}

function editLlama(document: LlamaDocument) {
  llamaForm.value = { ...document }
}

function resetLlamaForm() {
  llamaForm.value = {
    id: '',
    title: '',
    category: selectedCategory.value || 'rag',
    content: '',
  }
}

async function saveLlama() {
  if (!llamaForm.value.title.trim() || !llamaForm.value.content.trim() || !llamaForm.value.category.trim()) {
    ElMessage.warning('标题、分类、内容都要填')
    return
  }

  llamaSaving.value = true
  const payload = {
    title: llamaForm.value.title,
    category: llamaForm.value.category,
    content: llamaForm.value.content,
  }

  try {
    if (llamaForm.value.id) {
      await updateLlamaDocument(llamaForm.value.id, payload)
      ElMessage.success('LlamaIndex update_ref_doc 完成')
    } else {
      await createLlamaDocument(payload)
      ElMessage.success('LlamaIndex insert 完成')
    }
    resetLlamaForm()
    await refreshLlama()
  } finally {
    llamaSaving.value = false
  }
}

async function removeLlama(id: string) {
  await deleteLlamaDocument(id)
  ElMessage.success('LlamaIndex delete_ref_doc 完成')
  await refreshLlama()
}

async function runLlamaSearch() {
  const result = await searchLlamaDocuments(llamaQuery.value, selectedCategory.value || undefined)
  llamaHits.value = result.hits
}

async function handleSend() {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true

  try {
    const response = await sendMessage(text, useAgent.value)
    messages.value.push({
      role: 'assistant',
      content: response.answer,
      mode: response.mode,
      sources: response.sources,
    })
  } catch {
    messages.value.push({
      role: 'assistant',
      content: '请求失败。请先确认后端服务正在 http://127.0.0.1:8000 运行。',
      mode: 'error',
    })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([refreshDocuments(), refreshLlama()])
})
</script>

<template>
  <main class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">
          <el-icon><Collection /></el-icon>
        </div>
        <div>
          <h1>Mini RAG Agent</h1>
          <p>Python + LangChain 学习项目</p>
        </div>
      </div>

      <label class="upload-button">
        <el-icon><DocumentAdd /></el-icon>
        <span>{{ uploading ? '索引中...' : '上传文档' }}</span>
        <input :disabled="uploading" type="file" accept=".txt,.md,.pdf" @change="handleUpload" />
      </label>

      <section class="panel documents-panel">
        <div class="panel-title">
          <el-icon><Files /></el-icon>
          <span>Documents</span>
        </div>

        <div v-if="documents.length === 0" class="empty-state">
          上传一份资料，然后开始提问。
        </div>
        <div v-else class="document-list">
          <article v-for="document in documents" :key="document.id" class="document-row">
            <div>
              <strong>{{ document.filename }}</strong>
              <span>{{ document.chunks }} chunks · {{ document.characters }} chars</span>
            </div>
            <el-button :icon="Delete" circle text @click="handleDelete(document.id)" />
          </article>
        </div>
      </section>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <h2>Chat</h2>
          <p>上传、检索、回答、展示引用来源。</p>
        </div>
        <el-switch v-model="useAgent" active-text="Agent" inactive-text="RAG" />
      </header>

      <section class="chat-window">
        <article
          v-for="(message, index) in messages"
          :key="index"
          class="message"
          :class="message.role"
        >
          <div class="avatar">
            <el-icon v-if="message.role === 'assistant'"><Monitor /></el-icon>
            <el-icon v-else><ChatDotRound /></el-icon>
          </div>
          <div class="bubble">
            <div class="message-meta">
              <span>{{ message.role === 'assistant' ? 'Assistant' : 'You' }}</span>
              <em v-if="message.mode">{{ message.mode }}</em>
            </div>
            <p>{{ message.content }}</p>
            <div v-if="message.sources?.length" class="sources">
              <strong>Sources</strong>
              <div v-for="source in message.sources" :key="`${source.document_id}-${source.chunk_index}`">
                {{ source.filename }} #{{ source.chunk_index }} · score {{ source.score }}
                <span>{{ source.preview }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>

      <footer class="composer">
        <el-input
          v-model="input"
          :disabled="loading"
          size="large"
          placeholder="问一个文档里的问题，例如：这份文档讲了什么？"
          @keyup.enter="handleSend"
        />
        <el-button :loading="loading" type="primary" :icon="Promotion" @click="handleSend">
          发送
        </el-button>
      </footer>
    </section>

    <aside class="run-notes">
      <div class="llama-head">
        <div>
          <h2>LlamaIndex CRUD</h2>
          <p>分类 + 增删改查 + 检索</p>
        </div>
        <el-icon><Clock /></el-icon>
      </div>

      <div class="llama-filter">
        <el-select v-model="selectedCategory" clearable placeholder="全部分类" @change="refreshLlama">
          <el-option v-for="category in llamaCategories" :key="category" :label="category" :value="category" />
        </el-select>
      </div>

      <section class="llama-form">
        <el-input v-model="llamaForm.title" placeholder="标题" />
        <el-input v-model="llamaForm.category" placeholder="分类，例如 rag / agent" />
        <el-input
          v-model="llamaForm.content"
          type="textarea"
          :rows="5"
          placeholder="内容会写入 LlamaIndex Document"
        />
        <div class="llama-actions">
          <el-button text @click="resetLlamaForm">新建</el-button>
          <el-button type="primary" :loading="llamaSaving" @click="saveLlama">
            {{ llamaForm.id ? '更新' : '创建' }}
          </el-button>
        </div>
      </section>

      <section class="llama-list">
        <article v-for="document in llamaDocuments" :key="document.id" class="llama-row">
          <div>
            <strong>{{ document.title }}</strong>
            <span>{{ document.category }}</span>
          </div>
          <div class="row-tools">
            <el-button :icon="Edit" circle text @click="editLlama(document)" />
            <el-button :icon="Delete" circle text @click="removeLlama(document.id)" />
          </div>
        </article>
        <div v-if="llamaDocuments.length === 0" class="empty-state compact">还没有 LlamaIndex 文档。</div>
      </section>

      <section class="llama-search">
        <el-input v-model="llamaQuery" placeholder="检索 LlamaIndex 文档" @keyup.enter="runLlamaSearch">
          <template #append>
            <el-button :icon="Search" @click="runLlamaSearch" />
          </template>
        </el-input>
        <div v-for="hit in llamaHits" :key="hit.document_id" class="hit-row">
          <strong>{{ hit.title }}</strong>
          <span>{{ hit.category }} · {{ hit.score?.toFixed(3) ?? 'n/a' }}</span>
          <p>{{ hit.preview }}</p>
        </div>
      </section>
    </aside>
  </main>
</template>
