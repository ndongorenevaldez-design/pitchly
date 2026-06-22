// Responsibility: Configure social practice sessions.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { SOCIAL_SCENARIOS } from '../constants'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Button } from '../components/ui/Button'

export function SocialSetup() {
  const navigate = useNavigate()
  const [scenario, setScenario] = useState(SOCIAL_SCENARIOS[0])

  function start() {
    navigate('/session', { state: { mode: 'social', scenario, durationS: 120 } })
  }

  return (
    <PageWrapper>
      <main className="page narrow">
        <h1>Social setup</h1>
        <div className="scenario-list">
          {SOCIAL_SCENARIOS.map((item) => (
            <button
              className={item === scenario ? 'selected' : ''}
              key={item}
              type="button"
              onClick={() => setScenario(item)}
            >
              {item}
            </button>
          ))}
        </div>
        <Button onClick={start}>Open session room</Button>
      </main>
    </PageWrapper>
  )
}
