import { supabase } from "./supabase"

const base = "/api/backend"

export async function api(path: string, options: RequestInit = {}) {
  const { data } = await supabase.auth.getSession()
  const headers = new Headers(options.headers)

  if (data.session?.access_token) {
    headers.set("Authorization", `Bearer ${data.session.access_token}`)
  }

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }

  const normalizedPath = path.startsWith("/") ? path : `/${path}`

  const response = await fetch(`${base}${normalizedPath}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Something went wrong." }))

    throw new Error(error.detail || "Something went wrong.")
  }

  return response.json()
}