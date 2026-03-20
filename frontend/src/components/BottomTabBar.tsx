import { useLocation, useNavigate } from 'react-router-dom'

interface BottomTabBarProps {
  onMicPress: () => void
}

export function BottomTabBar({ onMicPress }: BottomTabBarProps) {
  const location = useLocation()
  const navigate = useNavigate()

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-surface border-t border-gray-100 z-40"
         style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
      <div className="flex items-center justify-around h-16 max-w-lg mx-auto relative">
        {/* Dashboard tab */}
        <button
          onClick={() => navigate('/')}
          className={`flex flex-col items-center gap-0.5 px-4 py-2 ${isActive('/') ? 'text-accent' : 'text-muted'}`}
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span className="text-xs font-medium">Home</span>
        </button>

        {/* Mic FAB - center, elevated */}
        <button
          onClick={onMicPress}
          className="w-14 h-14 bg-accent rounded-full flex items-center justify-center shadow-elevated -mt-6 active:scale-95 transition-transform"
        >
          <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>

        {/* History tab */}
        <button
          onClick={() => navigate('/history')}
          className={`flex flex-col items-center gap-0.5 px-4 py-2 ${isActive('/history') ? 'text-accent' : 'text-muted'}`}
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-xs font-medium">History</span>
        </button>
      </div>
    </nav>
  )
}
