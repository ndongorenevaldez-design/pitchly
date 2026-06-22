// Responsibility: Centralize every backend HTTP call.
import axios from 'axios'
import { supabase } from '../lib/supabase'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  withCredentials: true,
})

client.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
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
}
