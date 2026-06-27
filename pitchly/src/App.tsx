// Responsibility: Define Pitchly routes and protected app navigation.
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import type { ReactElement } from 'react'
import { ConfigError } from './components/ConfigError'
import { AuthProvider } from './auth/AuthProvider'
import { getMissingEnvVars } from './lib/config'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { Dashboard } from './pages/Dashboard'
import { Home } from './pages/Home'
import { InterviewSetup } from './pages/InterviewSetup'
import { ModeSelection } from './pages/ModeSelection'
import { Processing } from './pages/Processing'
import { Results } from './pages/Results'
import { Session } from './pages/Session'
import { SocialSetup } from './pages/SocialSetup'
import { Admin } from './pages/Admin'
import { ForgotPassword } from './pages/auth/ForgotPassword'
import { Login } from './pages/auth/Login'
import { ResetPassword } from './pages/auth/ResetPassword'
import { SignUp } from './pages/auth/SignUp'
import { VerifyEmail } from './pages/auth/VerifyEmail'
import './App.css'

function protectedPage(page: ReactElement) {
  return <ProtectedRoute>{page}</ProtectedRoute>
}

export default function App() {
  const missingEnvVars = getMissingEnvVars()
  if (missingEnvVars.length > 0) {
    return <ConfigError missing={missingEnvVars} />
  }

  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/dashboard" element={protectedPage(<Dashboard />)} />
          <Route path="/modes" element={protectedPage(<ModeSelection />)} />
          <Route path="/interview-setup" element={protectedPage(<InterviewSetup />)} />
          <Route path="/social-setup" element={protectedPage(<SocialSetup />)} />
          <Route path="/session" element={protectedPage(<Session />)} />
          <Route path="/processing" element={protectedPage(<Processing />)} />
          <Route path="/results/:sessionId" element={protectedPage(<Results />)} />
          <Route path="/admin" element={protectedPage(<Admin />)} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
