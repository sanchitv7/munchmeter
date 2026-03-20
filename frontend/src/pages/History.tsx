import { useEffect, useRef, useCallback } from 'react'
import { useHistory } from '../hooks/useHistory'
import { MealCard } from '../components/MealCard'

export function History() {
  const { days, loading, hasMore, loadMore, refresh, initialLoaded } = useHistory()
  const sentinelRef = useRef<HTMLDivElement>(null)

  // Initial load
  useEffect(() => {
    if (!initialLoaded) refresh()
  }, [initialLoaded, refresh])

  // Infinite scroll via IntersectionObserver
  const observerCallback = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      if (entries[0].isIntersecting && hasMore && !loading) {
        loadMore()
      }
    },
    [hasMore, loading, loadMore]
  )

  useEffect(() => {
    const sentinel = sentinelRef.current
    if (!sentinel) return
    const observer = new IntersectionObserver(observerCallback, { threshold: 0.1 })
    observer.observe(sentinel)
    return () => observer.disconnect()
  }, [observerCallback])

  const formatDateHeader = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00')
    const today = new Date()
    const yesterday = new Date()
    yesterday.setDate(today.getDate() - 1)

    const todayStr = today.toISOString().split('T')[0]
    const yesterdayStr = yesterday.toISOString().split('T')[0]

    if (dateStr === todayStr) return 'Today'
    if (dateStr === yesterdayStr) return 'Yesterday'

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <div className="px-5 pt-6 pb-4">
      <h1 className="text-2xl font-bold text-text mb-6">History</h1>

      {!loading && days.length === 0 && (
        <div className="text-center py-16">
          <p className="text-4xl mb-3">📋</p>
          <p className="text-text font-medium">No meals logged yet</p>
          <p className="text-muted text-sm mt-1">Your meal history will appear here</p>
        </div>
      )}

      <div className="space-y-6">
        {days.map((day) => (
          <div key={day.date}>
            {/* Sticky date header */}
            <div className="sticky top-0 z-10 bg-background py-2">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-text">{formatDateHeader(day.date)}</h2>
                <span className="text-sm text-muted">{Math.round(day.total_calories)} cal</span>
              </div>
            </div>

            <div className="space-y-3">
              {day.meals.map(meal => (
                <MealCard key={meal.id} meal={meal} />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Infinite scroll sentinel */}
      <div ref={sentinelRef} className="h-4" />

      {loading && (
        <div className="flex justify-center py-6">
          <div className="w-6 h-6 border-3 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  )
}
