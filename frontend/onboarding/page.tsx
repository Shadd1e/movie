'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '../../lib/supabase'
import { api } from '../../lib/api'

const genres = ['Drama', 'Comedy', 'Mystery', 'Thriller', 'Romance', 'History', 'Family', 'Adventure', 'Crime', 'Documentary', 'Science Fiction', 'Action', 'Musical', 'War', 'Western', 'Animation']
const yearOptions = [
  { value: 'before_1980', label: 'Before 1980' },
  { value: '1980_1999', label: '1980–1999' },
  { value: '2000_2009', label: '2000–2009' },
  { value: '2010_2019', label: '2010–2019' },
  { value: '2020_onwards', label: '2020 onwards' },
]
const ages = ['60–69', '70–79', '80+']

export default function Onboarding() {
  const [name, setName] = useState('')
  const [age, setAge] = useState('')
  const [region, setRegion] = useState('')
  const [country, setCountry] = useState('Nigeria')
  const [chosenGenres, setChosenGenres] = useState<string[]>([])
  const [years, setYears] = useState<string[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    let active = true
    supabase.auth.getSession().then(async ({ data }) => {
      if (!active) return
      if (!data.session) { router.replace('/login'); return }
      try {
        const profile = await api<any>('/profile')
        if (!active) return
        setName(profile.name || data.session.user.user_metadata?.display_name || '')
        setAge(profile.age_group || '')
        setRegion(profile.region || '')
        setCountry(profile.country || 'Nigeria')
        setChosenGenres(profile.genres || [])
        setYears(profile.preferred_movie_years || [])
      } catch (e) {
        if (active && e instanceof Error && !e.message.includes('profile could not be loaded')) setError(e.message)
      }
    })
    return () => { active = false }
  }, [router])

  function toggle<T extends string>(value: T, current: T[], setter: (next: T[]) => void) {
    setter(current.includes(value) ? current.filter((x) => x !== value) : [...current, value])
  }

  async function save() {
    setError('')
    if (!age) { setError('Please choose your age range.'); return }
    if (chosenGenres.length === 0) { setError('Choose at least one genre so we can begin personalising your recommendations.'); return }
    setBusy(true)
    try {
      await api('/onboarding', { method: 'POST', body: JSON.stringify({
        name: name.trim() || null,
        age_group: age,
        region: region.trim() || null,
        country: country.trim() || null,
        genres: chosenGenres,
        preferred_movie_years: years,
      }) })
      router.push('/recommendations')
    } catch (e) { setError(e instanceof Error ? e.message : 'We could not save your preferences.') }
    finally { setBusy(false) }
  }

  return <main className="form wide page-panel">
    <div className="eyebrow">Make it yours</div>
    <h1>Tell us what you enjoy.</h1>
    <p className="intro-copy">A few details help Maple Movies find films that are more relevant to you. You can change these choices at any time.</p>

    <section className="profile-section">
      <h2>Personal information</h2>
      <div className="field-grid">
        <div><label className="label" htmlFor="name">Name</label><input id="name" className="input" value={name} onChange={e => setName(e.target.value)} placeholder="Your name" autoComplete="name" /></div>
        <div><label className="label" htmlFor="age">Age range</label><select id="age" className="input" value={age} onChange={e => setAge(e.target.value)}><option value="">Choose your age range</option>{ages.map(a => <option key={a} value={a}>{a}</option>)}</select></div>
        <div><label className="label" htmlFor="region">Region / state</label><input id="region" className="input" value={region} onChange={e => setRegion(e.target.value)} placeholder="e.g. Delta State" /></div>
        <div><label className="label" htmlFor="country">Country</label><input id="country" className="input" value={country} onChange={e => setCountry(e.target.value)} placeholder="Your country" autoComplete="country-name" /></div>
      </div>
    </section>

    <section className="profile-section">
      <h2>Genres you enjoy</h2><p className="small">Select as many as you like.</p>
      <div className="choices">{genres.map(g => <button type="button" className={`choice ${chosenGenres.includes(g) ? 'selected' : ''}`} aria-pressed={chosenGenres.includes(g)} onClick={() => toggle(g, chosenGenres, setChosenGenres)} key={g}>{g}</button>)}</div>
    </section>

    <section className="profile-section">
      <h2>Preferred movie years</h2><p className="small">Choose the release periods you usually enjoy. These preferences help rank your recommendations.</p>
      <div className="year-options">{yearOptions.map(y => <label className={`year-option ${years.includes(y.value) ? 'selected' : ''}`} key={y.value}><input type="checkbox" checked={years.includes(y.value)} onChange={() => toggle(y.value, years, setYears)} /><span>{y.label}</span></label>)}</div>
    </section>

    {error && <p className="error" role="alert">{error}</p>}
    <div className="actions"><button className="button" onClick={save} disabled={busy}>{busy ? 'Saving your choices…' : 'Save preferences'}</button><button className="button secondary" onClick={() => router.push('/')} disabled={busy}>Not now</button></div>
    <p className="small privacy-note">Your choices are saved to your account and used to personalise movie recommendations.</p>
  </main>
}
