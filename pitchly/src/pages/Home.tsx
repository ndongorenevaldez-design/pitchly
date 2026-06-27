// Responsibility: Introduce Pitchly and route users into the product.
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { SLOGAN } from '../constants'
import { Button } from '../components/ui/Button'

export function Home() {
  return (
    <main className="home">
      <motion.section
        className="home-hero"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <h1>Pitchly</h1>
        <p style={{ fontSize: '1.15rem', maxWidth: 560, marginBottom: 32 }}>{SLOGAN}</p>
        <div className="hero-actions">
          <Link to="/signup">
            <Button>Get started free</Button>
          </Link>
          <Link to="/login">
            <Button variant="secondary">Sign in</Button>
          </Link>
        </div>
      </motion.section>
      <motion.section
        className="mode-preview"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
      >
        <article>
          <div style={{ color: 'var(--blue)', fontSize: '1.5rem', marginBottom: 8 }}>&#x1F3A4;</div>
          <h2>Interview Mode</h2>
          <p>Master job interviews with AI-powered feedback on clarity, structure, and confidence.</p>
        </article>
        <article>
          <div style={{ color: 'var(--green)', fontSize: '1.5rem', marginBottom: 8 }}>&#x1F4AC;</div>
          <h2>Social Mode</h2>
          <p>Build confidence in everyday conversations, networking, and group speaking.</p>
        </article>
      </motion.section>
    </main>
  )
}
