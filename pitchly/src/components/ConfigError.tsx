// Responsibility: Show a readable setup error when required env vars are missing.
type ConfigErrorProps = {
  missing: string[]
}

export function ConfigError({ missing }: ConfigErrorProps) {
  return (
    <main className="config-error">
      <section>
        <h1>Pitchly needs configuration</h1>
        <p>
          The app loaded, but required Vercel environment variables are missing.
          Add them in Project Settings → Environment Variables, then redeploy.
        </p>
        <ul>
          {missing.map((name) => (
            <li key={name}>
              <code>{name}</code>
            </li>
          ))}
        </ul>
        <p className="muted">
          Also set <code>VITE_API_URL</code> to your Railway backend URL, for example{' '}
          <code>https://your-service.up.railway.app</code>.
        </p>
      </section>
    </main>
  )
}
