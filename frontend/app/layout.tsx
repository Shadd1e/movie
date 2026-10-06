import './globals.css'
import Link from 'next/link'
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body><div className="shell"><nav className="nav"><div className="brand">Maple Movies</div><div className="navlinks"><Link href="/recommendations">For you</Link><Link href="/movies">Movies</Link><Link href="/profile">Profile</Link></div></nav>{children}<footer className="footer">A student project in movie recommendation. Movie information is supplied through TMDB.</footer></div></body></html>}
