// Responsibility: Hold current practice setup across setup and recording screens.
import { useMemo, useState } from 'react'

export type PracticeMode = 'interview' | 'social'

export type PracticeConfig = {
  mode: PracticeMode
  jobTitle?: string
  scenario?: string
  durationS: number
  difficulty?: string
}

export function useSessionState() {
  const [config, setConfig] = useState<PracticeConfig>({
    mode: 'interview',
    durationS: 120,
    difficulty: 'balanced',
  })
  return useMemo(() => ({ config, setConfig }), [config])
}
