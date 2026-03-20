import { useState, useCallback, useRef } from 'react'
import { getHistory } from '../api/client'
import type { DaySummary } from '../types'

const PAGE_SIZE = 20

export function useHistory() {
  const [days, setDays] = useState<DaySummary[]>([])
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const offset = useRef(0)
  const initialLoaded = useRef(false)

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return
    setLoading(true)
    setError(null)
    try {
      const result = await getHistory(offset.current, PAGE_SIZE)
      setDays(prev => [...prev, ...result.days])
      setHasMore(result.has_more)
      offset.current += PAGE_SIZE
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }, [loading, hasMore])

  const refresh = useCallback(async () => {
    offset.current = 0
    setDays([])
    setHasMore(true)
    setLoading(true)
    setError(null)
    try {
      const result = await getHistory(0, PAGE_SIZE)
      setDays(result.days)
      setHasMore(result.has_more)
      offset.current = PAGE_SIZE
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load history')
    } finally {
      setLoading(false)
      initialLoaded.current = true
    }
  }, [])

  return { days, loading, hasMore, error, loadMore, refresh, initialLoaded: initialLoaded.current }
}
