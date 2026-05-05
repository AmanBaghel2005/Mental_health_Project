import React, { useState } from 'react'
import Login from './Login.jsx'
import AgeSelection from './AgeSelection.jsx'
import Session from './Session.jsx'
import Results from './Results.jsx'

export default function App() {
  const [step, setStep] = useState('login')
  const [email, setEmail] = useState('')
  const [ageGroup, setAgeGroup] = useState('')
  const [results, setResults] = useState(null)

  const handleLoginSuccess = (userEmail) => {
    setEmail(userEmail)
    setStep('age-selection')
  }

  const handleAgeSelect = (selectedAge) => {
    setAgeGroup(selectedAge)
    setStep('session')
  }

  const handleSessionEnd = (sessionResults) => {
    setResults(sessionResults)
    setStep('result')
  }

  const handleReset = () => {
    setStep('age-selection')
    setResults(null)
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {step === 'login' && <Login onLoginSuccess={handleLoginSuccess} />}
      {step === 'age-selection' && <AgeSelection email={email} onSelect={handleAgeSelect} />}
      {step === 'session' && <Session ageGroup={ageGroup} onSessionEnd={handleSessionEnd} />}
      {step === 'result' && <Results results={results} onReset={handleReset} />}
    </div>
  )
}
