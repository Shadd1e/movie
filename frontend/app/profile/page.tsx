'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '../../lib/supabase'
import { api } from '../../lib/api'

const yearLabels: Record<string, string> = {
  before_1980: 'Before 1980', '1980_1999': '1980–1999', '2000_2009': '2000–2009',
  '2010_2019': '2010–2019', '2020_onwards': '2020 onwards',
}

export default function Profile() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [age, setAge] = useState('')
  const [region, setRegion] = useState('')
  const [country, setCountry] = useState('Nigeria')
  const [genres, setGenres] = useState<string[]>([])
  const [years, setYears] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const router = useRouter()

  useEffect(() => {
    let active = true
    async function load() {
      const { data } = await supabase.auth.getSession()
      if (!data.session) { router.replace('/login'); return }
      if (!active) return
      setEmail(data.session.user.email || '')
      try {
        const p = await api<any>('/profile')
        if (!active) return
        setName(p.name || data.session.user.user_metadata?.display_name || '')
        setAge(p.age_group || '')
        setRegion(p.region || '')
        setCountry(p.country || 'Nigeria')
        setGenres(p.genres || [])
        setYears(p.preferred_movie_years || [])
      } catch (e) { if (active) setError(e instanceof Error ? e.message : 'Profile could not be loaded.') }
      finally { if (active) setLoading(false) }
    }
    load()
    return () => { active = false }
  }, [router])

  async function save(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError(''); setNotice('')
    try {
      await api('/profile', { method: 'PATCH', body: JSON.stringify({ name: name.trim() || null, age_group: age || null, region: region.trim() || null, country: country.trim() || null, genres, preferred_movie_years: years }) })
      setNotice('Your profile and movie preferences have been saved.')
    } catch (err) { setError(err instanceof Error ? err.message : 'We could not save your profile.') }
    finally { setBusy(false) }
  }

  async function logout() { await supabase.auth.signOut(); router.replace('/login'); router.refresh() }
  const genreChoices = ['Drama', 'Comedy', 'Mystery', 'Thriller', 'Romance', 'History', 'Family', 'Adventure', 'Crime', 'Documentary', 'Science Fiction', 'Action', 'Musical', 'War', 'Western', 'Animation']
  const yearChoices = Object.entries(yearLabels)

  function toggle(value: string, list: string[], setter: (next: string[]) => void) { setter(list.includes(value) ? list.filter(x => x !== value) : [...list, value]) }

  return <main className="form wide page-panel">
    <div className="eyebrow">Your account</div><h1>My profile</h1><p className="intro-copy">Keep your details up to date so your movie suggestions continue to feel personal.</p>
    <div className="account-strip"><span className="avatar-mark">{(name || email || 'M').trim().charAt(0).toUpperCase()}</span><div><strong>{name || 'Maple Movies member'}</strong><div className="small">{email}</div></div></div>
    {loading ? <p>Loading your saved profile…</p> : <form onSubmit={save}>
      <section className="profile-section"><h2>Personal information</h2><div className="field-grid">
        <div><label className="label" htmlFor="profile-name">Name</label><input id="profile-name" className="input" value={name} onChange={e => setName(e.target.value)} placeholder="Your name" /></div>
        <div><label className="label" htmlFor="profile-age">Age range</label><select id="profile-age" className="input" value={age} onChange={e => setAge(e.target.value)}><option value="">Choose age range</option>{['60–69','70–79','80+'].map(a => <option key={a}>{a}</option>)}</select></div>
        <div><label className="label" htmlFor="profile-region">Region / state</label><input id="profile-region" className="input" value={region} onChange={e => setRegion(e.target.value)} placeholder="e.g. Delta State" /></div>
        <div><label className="label" htmlFor="profile-country">Country</label><input id="profile-country" className="input" value={country} onChange={e => setCountry(e.target.value)} placeholder="Your country" /></div>
      </div></section>
      <section className="profile-section"><h2>Preferred genres</h2><div className="choices">{genreChoices.map(g => <button type="button" key={g} aria-pressed={genres.includes(g)} className={`choice ${genres.includes(g) ? 'selected' : ''}`} onClick={() => toggle(g, genres, setGenres)}>{g}</button>)}</div></section>
      <section className="profile-section"><h2>Preferred movie years</h2><p className="small">These release periods are used to help rank your recommendations.</p><div className="year-options">{yearChoices.map(([value, label]) => <label className={`year-option ${years.includes(value) ? 'selected' : ''}`} key={value}><input type="checkbox" checked={years.includes(value)} onChange={() => toggle(value, years, setYears)} /><span>{label}</span></label>)}</div></section>
      {error && <p className="error" role="alert">{error}</p>}{notice && <p className="success" role="status">{notice}</p>}
      <div className="actions"><button className="button" disabled={busy}>{busy ? 'Saving…' : 'Save changes'}</button><Link className="button secondary button-link" href="/recommendations">View my recommendations</Link></div>
    </form>}
    <div className="profile-bottom"><button className="text-button" onClick={logout}>Sign out</button><Link href="/onboarding" className="text-link">Update setup choices</Link></div>
  </main>
}
