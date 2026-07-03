import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api',
  timeout: 60000,
})

export interface DocumentInfo {
  id: string
  filename: string
  chunks: number
  characters: number
}

export interface Source {
  document_id: string
  filename: string
  chunk_index: number
  score: number
  preview: string
}

export interface ChatResponse {
  answer: string
  sources: Source[]
  mode: string
}

export interface LlamaDocument {
  id: string
  title: string
  category: string
  content: string
}

export interface LlamaSearchHit {
  document_id: string
  title: string
  category: string
  score: number | null
  preview: string
}

export async function listDocuments() {
  const { data } = await api.get<DocumentInfo[]>('/documents')
  return data
}

export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post<{ document: DocumentInfo; message: string }>(
    '/documents/upload',
    formData,
  )
  return data
}

export async function deleteDocument(id: string) {
  await api.delete(`/documents/${id}`)
}

export async function sendMessage(message: string, useAgent: boolean) {
  const { data } = await api.post<ChatResponse>('/chat', { message, use_agent: useAgent })
  return data
}

export async function listLlamaCategories() {
  const { data } = await api.get<string[]>('/llama/categories')
  return data
}

export async function listLlamaDocuments(category?: string) {
  const { data } = await api.get<LlamaDocument[]>('/llama/documents', { params: { category } })
  return data
}

export async function createLlamaDocument(payload: Omit<LlamaDocument, 'id'>) {
  const { data } = await api.post<LlamaDocument>('/llama/documents', payload)
  return data
}

export async function updateLlamaDocument(id: string, payload: Omit<LlamaDocument, 'id'>) {
  const { data } = await api.put<LlamaDocument>(`/llama/documents/${id}`, payload)
  return data
}

export async function deleteLlamaDocument(id: string) {
  await api.delete(`/llama/documents/${id}`)
}

export async function searchLlamaDocuments(query: string, category?: string) {
  const { data } = await api.post<{ hits: LlamaSearchHit[]; note: string }>('/llama/search', {
    query,
    category: category || null,
    top_k: 5,
  })
  return data
}
