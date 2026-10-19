'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { supabase } from '../lib/supabase'
import { api } from '../lib/api'

type Rec = { movie: { id?: number | null; title: string; overview?: string; release_date?: string | null; genres?: string[]; poster_path?: string | null }; score?: number; reason?: string; signals?: unknown }
const poster = (path?: string | null) => path ? `https://image.tmdb.org/t/p/w500${path}` : ''

export default function Home() {
  const [session, setSession] = useState<any>(null)
  const [ready, setReady] = useState(false)
  const [recs, setRecs] = useState<Rec[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    supabase.auth.getSession().then(({ data }) => { if (active) { setSession(data.session); setReady(true) } })
    const { data: listener } = supabase.auth.onAuthStateChange((_event, current) => setSession(current))
    return () => { active = false; listener.subscription.unsubscribe() }
  }, [])

  async function load() {
    if (!session) return
    setLoading(true); setError('')
    try { const r = await api<{ recommendations?: Rec[] }>('/recommendations'); setRecs(r.recommendations || []) }
    catch (e) { setError(e instanceof Error ? e.message : 'Recommendations could not be loaded.') }
    finally { setLoading(false) }
  }
  useEffect(() => { if (session) load() }, [session])

  return <main>
    <section className="hero home-hero"><div className="hero-art" aria-hidden="true"><span className="hero-sun" /><span className="hero-hill hill-one" /><span className="hero-hill hill-two" /><span className="hero-poster poster-one">A story<br />to enjoy</span><span className="hero-poster poster-two">Your next<br />favourite</span></div>
      <div className="eyebrow">A calmer way to choose a movie</div><h1>Find something<br /><em>worth watching.</em></h1><p>Tell us what you enjoy. We narrow a big catalogue down to a few thoughtful choices, then explain why each film made the list.</p>
      <div className="actions"><Link className="button" href={session ? '/recommendations' : '/register'}>{session ? 'See my recommendations' : 'Get started'}</Link><Link className="button secondary button-link" href="/movies">Browse movies</Link></div>
      <div className="hero-note"><span className="note-dot" /> Simple choices. Personal suggestions. No endless scrolling.</div>
    </section>
    {ready && session && <section className="section"><div className="topline"><div><div className="eyebrow">A shortlist for you</div><h2>Movies worth a look</h2></div><button className="button secondary" onClick={load} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh'}</button></div>
      {error && <p className="error" role="alert">{error}</p>}
      {loading && <p>Finding films that fit your taste…</p>}
      {!loading && !error && recs.length > 0 && <div className="movie-grid recommendation-grid">{recs.slice(0,4).map((r,i)=><article className="movie-card recommendation-card" key={`${r.movie.id ?? r.movie.title}-${i}`}>{poster(r.movie.poster_path) ? <img className="poster" src={poster(r.movie.poster_path)} alt={`Poster for ${r.movie.title}`} loading="lazy"/> : <div className="poster poster-placeholder"><span>Maple<br/>Movies</span></div>}<div className="movie-copy"><div className="eyebrow">{r.movie.release_date?.slice(0,4) || 'For you'}</div><h3 className="movie-title">{r.movie.title}</h3><div className="meta">{(r.movie.genres || []).join(' · ')}</div><p>{r.movie.overview || 'A film worth discovering.'}</p><p className="reason">{r.reason}</p></div></article>)}</div>}
      {!loading && recs.length === 0 && <div className="notice-card"><h3>Let's tune your shortlist.</h3><p>Choose your preferred genres and movie years to help us find films to explore.</p><Link className="button" href="/onboarding">Set my preferences</Link></div>}
    </section>}
    <section className="section value-grid"><article className="value-card"><span className="value-number">01</span><h2>Easy to read</h2><p>Comfortable type, generous spacing and straightforward controls keep the focus on the story.</p></article><article className="value-card"><span className="value-number">02</span><h2>Personal from the start</h2><p>Choose genres and release periods before you have a long rating history.</p></article><article className="value-card"><span className="value-number">03</span><h2>A reason, not just a title</h2><p>Each suggestion comes with a short explanation so you can decide whether it sounds right for you.</p></article></section>
    {!session && ready && <section className="bottom-cta"><div><div className="eyebrow">Start with what you love</div><h2>Your next good movie is closer.</h2></div><Link className="button" href="/register">Create your account</Link></section>}
  </main>
}
