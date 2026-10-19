'use client'

import { FormEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '../../lib/supabase'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [register, setRegister] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const router = useRouter()

  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError(''); setMessage('')
    try {
      if (register) {
        const result = await supabase.auth.signUp({ email: email.trim(), password, options: { data: { display_name: name.trim() } } })
        if (result.error) throw result.error
        if (!result.data.session) {
          setMessage('Your account has been created. Check your email to confirm your address, then sign in.')
          setRegister(false)
          return
        }
        router.push('/onboarding'); router.refresh()
      } else {
        const result = await supabase.auth.signInWithPassword({ email: email.trim(), password })
        if (result.error) throw result.error
        router.push('/'); router.refresh()
      }
    } catch (e) { setError(e instanceof Error ? e.message : 'We could not complete that request.') }
    finally { setBusy(false) }
  }

  return <main className="auth"><div className="form">
    <div className="eyebrow">Welcome to Maple Movies</div><h1>{register ? 'Let’s find your kind of film.' : 'Good to see you again.'}</h1>
    <p>{register ? 'Create an account, choose a few preferences, and start with a shortlist made for you.' : 'Sign in to return to your profile and your personal movie shortlist.'}</p>
    <form onSubmit={submit}>
      {register && <><label className="label" htmlFor="name">Your name</label><input id="name" className="input" value={name} onChange={e => setName(e.target.value)} autoComplete="name" placeholder="How should we address you?" required maxLength={100} /> </>}
      <label className="label" htmlFor="email">Email address</label><input id="email" className="input" type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
      <label className="label" htmlFor="password">Password</label><input id="password" className="input" type="password" autoComplete={register ? 'new-password' : 'current-password'} required minLength={8} value={password} onChange={e => setPassword(e.target.value)} placeholder="At least 8 characters" />
      {error && <p className="error" role="alert">{error}</p>}{message && <p className="success" role="status">{message}</p>}
      <button className="button full" disabled={busy}>{busy ? 'Please wait…' : register ? 'Create account' : 'Sign in'}</button>
    </form>
    <button className="text-button" onClick={() => { setRegister(!register); setError(''); setMessage('') }}>{register ? 'Already have an account? Sign in' : 'New to Maple Movies? Create an account'}</button>
    <div><Link className="text-link" href="/">← Back to home</Link></div>
  </div></main>
}
