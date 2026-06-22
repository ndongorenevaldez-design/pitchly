// Responsibility: Render animated score radar visualizations.

export function RadarChart({ scores }: { scores: Record<string, number> }) {
  const entries = Object.entries(scores)
  const center = 150
  const radius = 104
  const points = entries.map(([, score], index) => {
    const angle = (Math.PI * 2 * index) / entries.length - Math.PI / 2
    const distance = radius * (score / 100)
    return `${center + Math.cos(angle) * distance},${center + Math.sin(angle) * distance}`
  })
  const grid = [0.25, 0.5, 0.75, 1].map((scale) =>
    entries
      .map(([,], index) => {
        const angle = (Math.PI * 2 * index) / entries.length - Math.PI / 2
        return `${center + Math.cos(angle) * radius * scale},${
          center + Math.sin(angle) * radius * scale
        }`
      })
      .join(' '),
  )

  return (
    <div className="radar-wrap">
      <svg viewBox="0 0 300 300" role="img" aria-label="Pitchly score radar chart">
        {grid.map((polygon) => (
          <polygon className="radar-grid" key={polygon} points={polygon} />
        ))}
        {entries.map(([label], index) => {
          const angle = (Math.PI * 2 * index) / entries.length - Math.PI / 2
          return (
            <text
              className="radar-label"
              key={label}
              x={center + Math.cos(angle) * 130}
              y={center + Math.sin(angle) * 130}
              textAnchor="middle"
              dominantBaseline="middle"
            >
              {label}
            </text>
          )
        })}
        <polygon className="radar-shape" points={points.join(' ')} />
      </svg>
    </div>
  )
}
