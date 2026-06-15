const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export function getApiUrl(path = '') {
  return `${apiUrl}${path.startsWith('/') ? path : `/${path}`}`
}
