'use client'

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '../../lib/supabase'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const router = useRouter()

  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError(''); setMessage('')
    try {
      const result = await supabase.auth.signInWithPassword({ email: email.trim(), password })
      if (result.error) throw result.error
      router.push('/'); router.refresh()
    } catch (e) { setError(e instanceof Error ? e.message : 'We could not sign you in. Please try again.') }
    finally { setBusy(false) }
  }

  async function resetPassword() {
    setError(''); setMessage('')
    if (!email.trim()) { setError('Enter your email address first, then choose forgot password.'); return }
    const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), { redirectTo: `${window.location.origin}/login` })
    if (error) setError(error.message)
    else setMessage('If an account exists for that address, a password reset email is on its way.')
  }

  return <main className="auth"><div className="form">
    <div className="eyebrow">Your next story starts here</div><h1>Welcome <em>back.</em></h1>
    <p>Sign in to return to your personal shortlist, saved preferences and movie discoveries.</p>
    <form onSubmit={submit}>
      <label className="label" htmlFor="email">Email address</label><input id="email" className="input" type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
      <label className="label" htmlFor="password">Password</label><input id="password" className="input" type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="Your password" />
      {error && <p className="error" role="alert">{error}</p>}{message && <p className="success" role="status">{message}</p>}
      <button className="button full" disabled={busy}>{busy ? 'Signing you in…' : 'Sign in to Maple Movies'}</button>
    </form>
    <button className="text-button" type="button" onClick={resetPassword}>Forgot password?</button>
    <div className="auth-switch">New to Maple Movies? <Link href="/register">Create your account</Link></div>
    <div style={{marginTop:18}}><Link className="text-link" href="/">← Back to home</Link></div>
  </div></main>
}
