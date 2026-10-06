'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { supabase } from '../lib/supabase'
import { api } from '../lib/api'

type Rec = { movie:any; score:number; reason?:string; signals:any }

export default function Home(){
  const [session,setSession]=useState<any>(null)
  const [recs,setRecs]=useState<Rec[]>([])
  const [loading,setLoading]=useState(false)
  useEffect(()=>{supabase.auth.getSession().then(({data})=>setSession(data.session))},[])
  async function load(){
    if(!session) return
    setLoading(true); try { const r=await api('/recommendations'); setRecs(r.recommendations||[]) } finally { setLoading(false) }
  }
  useEffect(()=>{ if(session) load() },[session])
  return <main>
    <section className="hero">
      <div className="eyebrow">A calmer way to choose a movie</div>
      <h1>Find something worth watching.</h1>
      <p>Tell us what you enjoy. We narrow a big catalogue down to a few choices that make sense, then tell you why each one made the list.</p>
      <div className="actions"><Link className="button" href={session?'/onboarding':'/login'}>{session?'Shape your choices':'Get started'}</Link><Link className="button secondary" href="/movies">Browse movies</Link></div>
    </section>
    {session && <section className="section">
      <div className="topline"><div><div className="eyebrow">For you</div><h2>Movies worth a look</h2></div><button className="button secondary" onClick={load}>{loading?'Refreshing…':'Refresh'}</button></div>
      <div className="movie-grid">{recs.map(r=><article className="movie-card" key={r.movie.id}><div className="movie-copy"><h3>{r.movie.title}</h3><div className="meta">{r.movie.release_date?.slice(0,4) || 'Year unavailable'} · {(r.movie.genres||[]).slice(0,3).join(' · ')}</div><p>{r.movie.overview || 'No summary is available yet.'}</p><div className="reason"><strong>Why it is here:</strong> {r.reason}</div></div></article>)}</div>
      {!loading && recs.length===0 && <div className="card"><h3>We need a little more to work with.</h3><p>Pick a few genres or favourite films and we can start building your recommendations.</p><Link className="button" href="/onboarding">Choose preferences</Link></div>}
    </section>}
    <section className="section grid"><div className="card"><h2>Easy to read</h2><p>Clear type, comfortable spacing and straightforward controls. Nothing important is hidden behind tiny icons.</p></div><div className="card"><h2>Personal from the start</h2><p>Choose a few genres and favourite films before you have any rating history.</p></div><div className="card"><h2>A reason, not just a title</h2><p>Recommendations come with a short explanation grounded in the information the system actually used.</p></div></section>
  </main>
}
