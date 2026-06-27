// Responsibility: Centralize every backend HTTP call.
import axios from 'axios'
import { getClientConfig } from '../lib/config'
import { getSupabase } from '../lib/supabase'

const client = axios.create({
  baseURL: getClientConfig()?.apiUrl ?? 'http://localhost:8000',
  withCredentials: true,
})

client.interceptors.request.use(async (config) => {
  const { data } = await getSupabase().auth.getSession()
  const token = data.session?.access_token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const api = {
  analyzeSession: (data: unknown) => client.post('/session/analyze', data),
  uploadVideo: (sessionId: string, formData: FormData) =>
    client.post(`/upload/${sessionId}`, formData),
  getStatus: (jobId: string) => client.get(`/session/status/${jobId}`),
  getResults: (sessionId: string) => client.get(`/results/${sessionId}`),
  getDashboard: () => client.get('/dashboard'),
  generateQuestions: (data: unknown) => client.post('/session/questions', data),
  // Admin
  getAdminStats: () => client.get('/admin/stats'),
  getAdminUsers: () => client.get('/admin/users'),
  getAdminSessions: (limit = 50) => client.get(`/admin/sessions?limit=${limit}`),
  getAdminResults: (limit = 50) => client.get(`/admin/results?limit=${limit}`),
  getAdminSessionDetail: (id: string) => client.get(`/admin/sessions/${id}`),
}
