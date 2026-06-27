import { createClient, type SupabaseClient } from '@supabase/supabase-js'
import { getClientConfig } from './config'

let supabaseClient: SupabaseClient | null = null

export function getSupabase(): SupabaseClient {
  if (!supabaseClient) {
    const config = getClientConfig()
    if (!config) {
      throw new Error('Supabase is not configured')
    }
    supabaseClient = createClient(config.supabaseUrl, config.supabaseAnonKey)
  }
  return supabaseClient
}
