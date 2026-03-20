import { useState, useEffect, useCallback } from 'react'
import { getMeals } from '../api/client'
import type { DayMeals } from '../types'

export function useMeals(date: string) {
  const [data, setData] = useState<DayMeals | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await getMeals(date)
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load meals')
    } finally {
      setLoading(false)
    }
  }, [date])

  useEffect(() => {
    refresh()
  }, [refresh])

  return { data, loading, error, refresh }
}
