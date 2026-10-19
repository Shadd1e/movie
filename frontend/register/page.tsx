'use client'

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '../../lib/supabase'

export default function Register() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const router = useRouter()

  async function submit(e: FormEvent) {
    e.preventDefault(); setError(''); setMessage('')
    if (password.length < 8) { setError('Use a password with at least 8 characters.'); return }
    if (password !== confirm) { setError('Your passwords do not match.'); return }
    setBusy(true)
    try {
      const result = await supabase.auth.signUp({ email: email.trim(), password, options: { data: { display_name: name.trim(), name: name.trim() } } })
      if (result.error) throw result.error
      if (!result.data.session) {
        setMessage('Your account request is ready. Check your email to confirm your address, then sign in to continue setup.')
        return
      }
      router.push('/onboarding'); router.refresh()
    } catch (e) { setError(e instanceof Error ? e.message : 'We could not create your account. Please try again.') }
    finally { setBusy(false) }
  }

  return <main className="auth"><div className="form register-form">
    <div className="eyebrow">A more personal movie night</div><h1>Find your kind <em>of story.</em></h1>
    <p>Create your account, tell us a little about what you enjoy, and let Maple Movies help you find films worth your time.</p>
    <div className="register-benefits"><span>✦ Thoughtful recommendations</span><span>✦ Preferences you can change anytime</span></div>
    <form onSubmit={submit}>
      <label className="label" htmlFor="name">Your name</label><input id="name" className="input" value={name} onChange={e => setName(e.target.value)} autoComplete="name" placeholder="How should we address you?" required maxLength={100} />
      <label className="label" htmlFor="email">Email address</label><input id="email" className="input" type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
      <label className="label" htmlFor="password">Create password</label><input id="password" className="input" type="password" autoComplete="new-password" required minLength={8} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 8 characters" />
      <label className="label" htmlFor="confirm">Confirm password</label><input id="confirm" className="input" type="password" autoComplete="new-password" required minLength={8} value={confirm} onChange={e => setConfirm(e.target.value)} placeholder="Enter your password again" />
      {error && <p className="error" role="alert">{error}</p>}{message && <p className="success" role="status">{message}</p>}
      <button className="button full" disabled={busy}>{busy ? 'Creating your account…' : 'Create my account'}</button>
    </form>
    <div className="auth-switch">Already have an account? <Link href="/login">Sign in</Link></div>
    <div style={{marginTop:18}}><Link className="text-link" href="/">← Back to home</Link></div>
  </div></main>
}
