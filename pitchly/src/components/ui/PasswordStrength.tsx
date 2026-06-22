// Responsibility: Show live password strength feedback.
function getStrength(password: string) {
  const checks = [
    password.length >= 8,
    /[A-Z]/.test(password),
    /\d/.test(password),
    /[!@#$%^&*]/.test(password),
  ]
  return checks.filter(Boolean).length
}

export function PasswordStrength({ password }: { password: string }) {
  const score = getStrength(password)
  const labels = ['Weak', 'Weak', 'Fair', 'Strong', 'Very Strong']
  return (
    <div className="password-meter" data-score={score}>
      <div>
        <span style={{ width: `${Math.max(12, score * 25)}%` }} />
      </div>
      <small>{labels[score]}</small>
    </div>
  )
}
