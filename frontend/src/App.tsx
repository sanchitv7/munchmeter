import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-background text-text font-sans">
      <Routes>
        <Route path="/" element={<div className="p-6"><h1 className="text-2xl font-bold text-accent">MunchMeter</h1><p className="text-muted mt-2">Dashboard coming soon...</p></div>} />
        <Route path="/history" element={<div className="p-6"><h1 className="text-2xl font-bold">History</h1></div>} />
      </Routes>
    </div>
  )
}

export default App
