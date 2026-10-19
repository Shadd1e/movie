'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { api } from '../../lib/api'
import { supabase } from '../../lib/supabase'

type Movie = { id?: number | null; title: string; overview?: string; release_date?: string | null; genres?: string[]; poster_path?: string | null }
type Rec = { movie: Movie; reason?: string; score?: number; signals?: Record<string, unknown> }
const poster = (path?: string | null) => path ? `https://image.tmdb.org/t/p/w500${path}` : ''

export default function Recommendations() {
  const [items, setItems] = useState<Rec[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [ratingId, setRatingId] = useState<number | null>(null)
  const [rated, setRated] = useState<Record<number, number>>({})
  const router = useRouter()

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const { data } = await supabase.auth.getSession()
      if (!data.session) { router.replace('/login'); return }
      const result = await api<{ recommendations?: Rec[] }>('/recommendations')
      setItems((result.recommendations || []).filter(x => x && x.movie && x.movie.title))
    } catch (e) { setError(e instanceof Error ? e.message : 'Recommendations could not be loaded.') }
    finally { setLoading(false) }
  }, [router])
  useEffect(() => { load() }, [load])

  async function rate(id: number, value: number) {
    setRatingId(id); setError('')
    try { await api('/ratings', { method: 'POST', body: JSON.stringify({ movie_id: id, rating: value }) }); setRated(old => ({ ...old, [id]: value })) }
    catch (e) { setError(e instanceof Error ? e.message : 'Your rating could not be saved.') }
    finally { setRatingId(null) }
  }

  return <main>
    <section className="hero compact"><div className="eyebrow">Picked for you</div><h1>Something good is waiting.</h1><p>Explore a thoughtful shortlist. Each suggestion includes a reason it may be worth your time. Rate films to help shape future recommendations.</p><div className="actions"><button className="button secondary" onClick={load} disabled={loading}>{loading ? 'Finding films…' : 'Refresh suggestions'}</button><Link className="button secondary button-link" href="/profile">Edit preferences</Link></div></section>
    {loading && <div className="notice-card"><span className="loader" />Finding films that fit your taste…</div>}
    {error && <div className="error" role="alert">{error} {error.toLowerCase().includes('sign in') && <Link href="/login">Sign in</Link>}</div>}
    {!loading && !error && items.length === 0 && <div className="notice-card"><h2>Your shortlist is taking shape.</h2><p>We couldn't find recommendations just now. Check your preferences or try again.</p><div className="actions"><Link className="button" href="/onboarding">Set preferences</Link><button className="button secondary" onClick={load}>Try again</button></div></div>}
    <section className="movie-grid recommendation-grid">{items.map((item, index) => { const m = item.movie; return <article className="movie-card recommendation-card" key={`${m.id ?? m.title}-${index}`}>
      {poster(m.poster_path) ? <img className="poster" src={poster(m.poster_path)} alt={`Poster for ${m.title}`} loading="lazy" /> : <div className="poster poster-placeholder"><span>Maple<br />Movies</span></div>}
      <div className="movie-copy"><div className="eyebrow">{m.release_date?.slice(0,4) || 'A film to discover'}</div><h2 className="movie-title">{m.title}</h2><div className="meta">{(m.genres || []).join(' · ') || 'Recommended for you'}</div><p>{m.overview || 'A film selected for you to explore.'}</p><div className="reason"><strong>Why this may suit you</strong><p>{item.reason || 'A thoughtful pick from your current movie shortlist.'}</p></div>
      {m.id != null && <div className="rate-area"><span className="small">How would you rate it?</span><div className="rating-buttons" aria-label={`Rate ${m.title}`}>{[1,2,3,4,5].map(n => <button key={n} type="button" className={`star-button ${(rated[m.id!] || 0) >= n ? 'active' : ''}`} disabled={ratingId === m.id} onClick={() => rate(m.id!, n)} aria-label={`${n} out of 5 stars`}>★</button>)}</div>{rated[m.id] && <span className="small">Your rating: {rated[m.id]}/5</span>}</div>}
      </div></article> })}</section>
  </main>
}
