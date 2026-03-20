import { useState, useRef } from 'react'
import { Routes, Route } from 'react-router-dom'
import { BottomTabBar } from './components/BottomTabBar'
import { RecordingSheet } from './components/RecordingSheet'
import { Dashboard } from './pages/Dashboard'
import { History } from './pages/History'

function App() {
  const [sheetOpen, setSheetOpen] = useState(false)
  const refreshRef = useRef<(() => void) | null>(null)

  return (
    <div className="min-h-screen bg-background text-text font-sans pb-20">
      <Routes>
        <Route path="/" element={<Dashboard onRefreshRef={refreshRef} />} />
        <Route path="/history" element={<History />} />
      </Routes>

      <BottomTabBar onMicPress={() => setSheetOpen(true)} />

      <RecordingSheet
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        onSaved={() => refreshRef.current?.()}
      />
    </div>
  )
}

export default App
