'use client'

import { useEffect, useState } from 'react'
import { api } from '../../lib/api'
import Link from 'next/link'

type Rec = {
  movie: any
  reason: string
  score: number
}

export default function Recommendations() {
  const [items, setItems] = useState<Rec[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api('/recommendations')
      .then((x) => setItems(x.recommendations || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <main>
      <section className="hero">
        <div className="eyebrow">Your recommendations</div>
        <h1>Here are a few to try.</h1>
        <p>
          These are ranked from the information the system has about your tastes.
          As you rate more films, the list can become more personal.
        </p>
      </section>

      {loading && <p>Putting a shortlist together…</p>}
      {error && <div className="error">{error}</div>}

      {!loading && !error && items.length === 0 && (
        <div className="error">
          We could not find recommendations right now. Please try again in a moment.
        </div>
      )}

      <div className="grid">
        {items.map((x, index) => (
          <article className="card" key={`${x.movie.id ?? x.movie.title}-${index}`}>
            <h2 className="movie-title">{x.movie.title}</h2>
            <div className="meta">
              {x.movie.release_date?.slice(0, 4) || '—'} · {(x.movie.genres || []).join(', ') || 'Movie'}
            </div>
            <p>{x.movie.overview || 'No synopsis is available yet.'}</p>
            <p className="reason">{x.reason}</p>
            {x.movie.id != null && (
              <Link className="button secondary" href={`/movies?id=${x.movie.id}`}>
                See details
              </Link>
            )}
          </article>
        ))}
      </div>
    </main>
  )
}
