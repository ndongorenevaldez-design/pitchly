import { getClientConfig } from './config'

export function getApiUrl(path = '') {
  const config = getClientConfig()
  const apiUrl = config?.apiUrl ?? 'http://localhost:8000'
  return `${apiUrl}${path.startsWith('/') ? path : `/${path}`}`
}
