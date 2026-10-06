import { supabase } from "./supabase"
const base = process.env.NEXT_PUBLIC_API_URL!
export async function api(path: string, options: RequestInit = {}) {
  const { data } = await supabase.auth.getSession()
  const headers = new Headers(options.headers)
  if (data.session) headers.set("Authorization", `Bearer ${data.session.access_token}`)
  if (options.body) headers.set("Content-Type", "application/json")
  const r = await fetch(`${base}${path}`, { ...options, headers })
  if (!r.ok) { const e = await r.json().catch(() => ({ detail: "Something went wrong." })); throw new Error(e.detail || "Something went wrong.") }
  return r.json()
}
