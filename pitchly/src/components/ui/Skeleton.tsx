// Responsibility: Provide loading placeholders instead of blank spinners.
export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`skeleton ${className}`} aria-hidden="true" />
}

export function FullPageSkeleton() {
  return (
    <main className="full-skeleton">
      <Skeleton className="skeleton-title" />
      <Skeleton className="skeleton-line" />
      <Skeleton className="skeleton-line short" />
    </main>
  )
}
