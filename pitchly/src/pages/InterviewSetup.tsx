// Responsibility: Configure interview practice sessions.
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageWrapper } from '../components/layout/PageWrapper'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export function InterviewSetup() {
  const navigate = useNavigate()
  const [jobTitle, setJobTitle] = useState('Software Engineer Intern')

  function start() {
    navigate('/session', {
      state: { mode: 'interview', jobTitle, durationS: 120, difficulty: 'balanced' },
    })
  }

  return (
    <PageWrapper>
      <main className="page narrow">
        <h1>Interview setup</h1>
        <Input label="Target job" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
        <Button onClick={start}>Open session room</Button>
      </main>
    </PageWrapper>
  )
}
