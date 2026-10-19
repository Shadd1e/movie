import './globals.css'
import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Maple Movies — Find something worth watching',
  description: 'A calmer, more personal way to discover movies.',
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><div className="shell"><nav className="nav"><Link href="/" className="brand"><span className="brand-mark">M</span><span>Maple <span className="brand-light">Movies</span></span></Link><div className="navlinks"><Link href="/recommendations">For you</Link><Link href="/movies">Movies</Link><Link href="/profile">My profile</Link><Link href="/login">Sign in</Link><Link href="/register">Create account</Link></div></nav>{children}<footer className="footer"><span>Maple Movies</span><span>Thoughtful film discovery, one story at a time.</span><span>Movie information supplied through TMDB.</span></footer></div></body></html>
}
