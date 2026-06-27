// Responsibility: Validate frontend env config used at build and runtime.
export type ClientConfig = {
  supabaseUrl: string
  supabaseAnonKey: string
  apiUrl: string
}

function normalizeApiUrl(url: string) {
  return url.replace(/\/+$/, '')
}

export function getMissingEnvVars(): string[] {
  const missing: string[] = []
  if (!import.meta.env.VITE_SUPABASE_URL) missing.push('VITE_SUPABASE_URL')
  if (!import.meta.env.VITE_SUPABASE_ANON_KEY) missing.push('VITE_SUPABASE_ANON_KEY')
  return missing
}

export function getClientConfig(): ClientConfig | null {
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
  const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
  if (!supabaseUrl || !supabaseAnonKey) return null

  return {
    supabaseUrl,
    supabaseAnonKey,
    apiUrl: normalizeApiUrl(import.meta.env.VITE_API_URL ?? 'http://localhost:8000'),
  }
}
