'use client'

import { useState } from 'react'
import { api } from '../../lib/api'

type Movie = { id: number; title: string; overview?: string; release_date?: string; genre_ids?: number[]; genres?: string[]; poster_path?: string | null; vote_average?: number }
const genreNames: Record<number, string> = { 28:'Action',12:'Adventure',16:'Animation',35:'Comedy',80:'Crime',99:'Documentary',18:'Drama',10751:'Family',14:'Fantasy',36:'History',27:'Horror',10402:'Music',9648:'Mystery',10749:'Romance',878:'Science Fiction',10770:'TV Movie',53:'Thriller',10752:'War',37:'Western' }
const poster = (path?: string | null) => path ? `https://image.tmdb.org/t/p/w500${path}` : ''

export default function Movies() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState<Movie[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)
  const [selected, setSelected] = useState<Movie | null>(null)
  const [rating, setRating] = useState(0)
  const [savingRating, setSavingRating] = useState(false)
  const [notice, setNotice] = useState('')

  async function search(e?: React.FormEvent) {
    e?.preventDefault(); if (!q.trim()) return
    setBusy(true); setError(''); setNotice(''); setSearched(true); setSelected(null)
    try { const result = await api<{ results?: Movie[] }>(`/movies/search?q=${encodeURIComponent(q.trim())}`); setResults(result.results || []) }
    catch (err) { setError(err instanceof Error ? err.message : 'Search could not be completed.') }
    finally { setBusy(false) }
  }

  async function openMovie(movie: Movie) {
    setSelected(movie); setRating(0); setNotice(''); setError('')
    try { const detail = await api<Movie>(`/movies/${movie.id}`); setSelected({ ...movie, ...detail }) }
    catch { /* Search result remains available when details are not in the catalogue. */ }
  }

  async function saveRating() {
    if (!selected?.id || !rating) return
    setSavingRating(true); setError(''); setNotice('')
    try { await api('/ratings', { method: 'POST', body: JSON.stringify({ movie_id: selected.id, rating }) }); setNotice('Your rating has been saved and will help personalise future recommendations.') }
    catch (err) { setError(err instanceof Error ? err.message : 'Your rating could not be saved.') }
    finally { setSavingRating(false) }
  }

  return <main>
    <section className="hero compact"><div className="eyebrow">The movie shelf</div><h1>Find a film.</h1><p>Search by title, take a look at the story, and rate films you have watched. Your ratings help us make better suggestions.</p>
      <form className="search-row" onSubmit={search}><input className="input" value={q} onChange={e => setQ(e.target.value)} placeholder="Try a movie title" aria-label="Movie title" /><button className="button" disabled={busy || !q.trim()}>{busy ? 'Searching…' : 'Search movies'}</button></form>
    </section>
    {error && <p className="error" role="alert">{error}</p>}
    {notice && <p className="success" role="status">{notice}</p>}
    {selected && <section className="detail-panel"><button className="text-button" onClick={() => setSelected(null)}>← Back to results</button><div className="detail-layout">{poster(selected.poster_path) ? <img className="detail-poster" src={poster(selected.poster_path)} alt={`Poster for ${selected.title}`} /> : <div className="detail-poster poster-placeholder">Maple Movies</div>}<div><div className="eyebrow">{selected.release_date?.slice(0,4) || 'Movie details'}</div><h2>{selected.title}</h2><p>{selected.overview || 'A synopsis is not available for this title yet.'}</p><p className="meta">{(selected.genres || selected.genre_ids?.map(id => genreNames[id]).filter(Boolean) || []).join(' · ')}</p><div className="profile-section"><h3>Rate this film</h3><p className="small">Your rating helps improve future recommendations.</p><div className="rating-buttons">{[1,2,3,4,5].map(n => <button type="button" key={n} className={`star-button ${rating >= n ? 'active' : ''}`} onClick={() => setRating(n)} aria-label={`${n} out of 5 stars`}>★</button>)}</div><button className="button" onClick={saveRating} disabled={!rating || savingRating}>{savingRating ? 'Saving rating…' : 'Save rating'}</button></div></div></div></section>}
    {!selected && searched && !busy && !error && results.length === 0 && <div className="notice-card"><h2>No titles found</h2><p>Try a shorter title or check the spelling.</p></div>}
    {!selected && <section className="movie-grid browse-grid">{results.map(movie => { const genres = movie.genres || movie.genre_ids?.map(id => genreNames[id]).filter(Boolean) || []; return <article className="movie-card browse-card" key={movie.id}>
      {poster(movie.poster_path) ? <img className="poster" src={poster(movie.poster_path)} alt={`Poster for ${movie.title}`} loading="lazy" /> : <div className="poster poster-placeholder"><span>Maple<br />Movies</span></div>}
      <div className="movie-copy"><div className="eyebrow">{movie.release_date?.slice(0,4) || 'Release year unavailable'}</div><h2 className="movie-title">{movie.title}</h2><div className="meta">{genres.join(' · ') || 'Film'}</div><p>{movie.overview || 'No synopsis is available yet.'}</p><button className="button secondary" onClick={() => openMovie(movie)}>View details & rate</button></div>
    </article> })}</section>}
  </main>
}
