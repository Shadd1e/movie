import { supabase } from './supabase'

const base = '/api/backend'

export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
  if (sessionError) throw new Error('Your session could not be checked. Please sign in again.')

  const headers = new Headers(options.headers)
  if (sessionData.session?.access_token) headers.set('Authorization', `Bearer ${sessionData.session.access_token}`)
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  let response: Response
  try {
    response = await fetch(`${base}${normalizedPath}`, { ...options, headers, cache: 'no-store' })
  } catch {
    throw new Error('We could not reach the Maple Movies service. Please try again shortly.')
  }

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json().catch(() => ({}))
    : await response.text().catch(() => '')

  if (!response.ok) {
    const message = typeof payload === 'object' && payload
      ? payload.detail || payload.message || 'Something went wrong. Please try again.'
      : 'Something went wrong. Please try again.'
    if (response.status === 401) throw new Error('Your session has expired. Please sign in again.')
    throw new Error(String(message))
  }
  return payload as T
}
