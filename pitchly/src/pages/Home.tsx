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
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1>Pitchly</h1>
        <p>{SLOGAN}</p>
        <div className="hero-actions">
          <Link to="/signup">
            <Button>Start practicing</Button>
          </Link>
          <Link to="/login">
            <Button variant="secondary">Login</Button>
          </Link>
        </div>
      </motion.section>
      <section className="mode-preview">
        <article>Interview coaching</article>
        <article>Social confidence</article>
      </section>
    </main>
  )
}
