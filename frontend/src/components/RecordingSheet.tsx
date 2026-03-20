import { useState, useCallback } from 'react'
import { useRecorder } from '../hooks/useRecorder'
import { transcribe, extractIngredients, nutritionLookup, saveMeal } from '../api/client'
import { MealSlotPicker } from './MealSlotPicker'
import { QuantityPicker } from './QuantityPicker'
import { MacroSummary } from './MacroSummary'
import type { MealSlot, NutritionItem } from '../types'

type SheetState = 'slot-select' | 'recording' | 'processing' | 'review' | 'saving'

interface RecordingSheetProps {
  open: boolean
  onClose: () => void
  onSaved: () => void
}

export function RecordingSheet({ open, onClose, onSaved }: RecordingSheetProps) {
  const { elapsed, start, stop } = useRecorder()
  const [state, setState] = useState<SheetState>('slot-select')
  const [mealSlot, setMealSlot] = useState<MealSlot | null>(null)
  const [transcription, setTranscription] = useState('')
  const [items, setItems] = useState<NutritionItem[]>([])
  const [totals, setTotals] = useState({ calories: 0, protein: 0, carbs: 0, fat: 0 })
  const [editingIdx, setEditingIdx] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const reset = useCallback(() => {
    setState('slot-select')
    setMealSlot(null)
    setTranscription('')
    setItems([])
    setTotals({ calories: 0, protein: 0, carbs: 0, fat: 0 })
    setEditingIdx(null)
    setError(null)
  }, [])

  const handleClose = useCallback(() => {
    reset()
    onClose()
  }, [reset, onClose])

  const handleStartRecording = useCallback(async () => {
    if (!mealSlot) return
    setState('recording')
    await start()
  }, [mealSlot, start])

  const handleStopRecording = useCallback(async () => {
    const audioBlob = await stop()
    setState('processing')
    setError(null)

    try {
      const { text } = await transcribe(audioBlob)
      setTranscription(text)

      const { ingredients } = await extractIngredients(text)
      const nutrition = await nutritionLookup(ingredients)

      setItems(nutrition.items)
      setTotals({
        calories: nutrition.total_calories,
        protein: nutrition.total_protein,
        carbs: nutrition.total_carbs,
        fat: nutrition.total_fat,
      })
      setState('review')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Processing failed')
      setState('slot-select')
    }
  }, [stop])

  const handleQuantityChange = useCallback((idx: number, newQty: number) => {
    setItems(prev => {
      const updated = [...prev]
      const item = updated[idx]
      const ratio = newQty / item.quantity
      updated[idx] = {
        ...item,
        quantity: newQty,
        calories: item.calories * ratio,
        protein: item.protein * ratio,
        carbs: item.carbs * ratio,
        fat: item.fat * ratio,
      }
      // Recalculate totals
      const newTotals = updated.reduce(
        (acc, i) => ({
          calories: acc.calories + i.calories,
          protein: acc.protein + i.protein,
          carbs: acc.carbs + i.carbs,
          fat: acc.fat + i.fat,
        }),
        { calories: 0, protein: 0, carbs: 0, fat: 0 }
      )
      setTotals(newTotals)
      return updated
    })
    setEditingIdx(null)
  }, [])

  const handleSave = useCallback(async () => {
    if (!mealSlot) return
    setState('saving')
    try {
      const today = new Date().toISOString().split('T')[0]
      await saveMeal({
        date: today,
        meal_slot: mealSlot,
        transcription,
        items,
      })
      handleClose()
      onSaved()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed')
      setState('review')
    }
  }, [mealSlot, transcription, items, handleClose, onSaved])

  const formatElapsed = (s: number) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/40" onClick={handleClose} />

      {/* Sheet */}
      <div className="absolute bottom-0 left-0 right-0 bg-background rounded-t-3xl max-h-[85vh] overflow-y-auto"
           style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
        {/* Drag handle */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-10 h-1 bg-gray-300 rounded-full" />
        </div>

        <div className="px-6 pb-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>
          )}

          {/* SLOT SELECT */}
          {state === 'slot-select' && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-text text-center">Log a meal</h2>
              <div>
                <p className="text-sm text-muted mb-3">What meal is this?</p>
                <MealSlotPicker selected={mealSlot} onChange={setMealSlot} />
              </div>
              <button
                onClick={handleStartRecording}
                disabled={!mealSlot}
                className="w-full py-4 bg-accent text-white rounded-pill font-semibold text-lg disabled:opacity-40 transition-opacity"
              >
                Start Recording
              </button>
            </div>
          )}

          {/* RECORDING */}
          {state === 'recording' && (
            <div className="flex flex-col items-center py-8 space-y-6">
              {/* Pulsing circle */}
              <div className="relative">
                <div className="w-24 h-24 bg-accent/20 rounded-full animate-ping absolute" />
                <div className="w-24 h-24 bg-accent/30 rounded-full flex items-center justify-center relative">
                  <div className="w-16 h-16 bg-accent rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    </svg>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-lg font-medium text-text">Recording...</p>
                <p className="text-muted text-center">{formatElapsed(elapsed)}</p>
              </div>
              <button
                onClick={handleStopRecording}
                className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center shadow-lg"
              >
                <div className="w-6 h-6 bg-white rounded-sm" />
              </button>
            </div>
          )}

          {/* PROCESSING */}
          {state === 'processing' && (
            <div className="flex flex-col items-center py-12 space-y-4">
              <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin" />
              <p className="text-muted">Analyzing your meal...</p>
            </div>
          )}

          {/* REVIEW */}
          {state === 'review' && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-text">Review ingredients</h2>

              {transcription && (
                <p className="text-sm text-muted italic">"{transcription}"</p>
              )}

              <div className="space-y-2">
                {items.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between bg-surface rounded-xl p-3">
                    <div>
                      <span className="text-text font-medium">{item.ingredient_name}</span>
                      <span className="text-muted text-sm ml-2">{item.unit}</span>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); setEditingIdx(idx) }}
                      className="px-3 py-1 bg-accent/10 text-accent rounded-pill text-sm font-medium"
                    >
                      {item.quantity}
                    </button>
                  </div>
                ))}
              </div>

              <div className="bg-surface rounded-xl p-4">
                <MacroSummary
                  calories={totals.calories}
                  protein={totals.protein}
                  carbs={totals.carbs}
                  fat={totals.fat}
                />
              </div>

              <button
                onClick={handleSave}
                className="w-full py-4 bg-accent text-white rounded-pill font-semibold text-lg"
              >
                Save Meal
              </button>
            </div>
          )}

          {/* SAVING */}
          {state === 'saving' && (
            <div className="flex flex-col items-center py-12 space-y-4">
              <div className="w-12 h-12 border-4 border-accent border-t-transparent rounded-full animate-spin" />
              <p className="text-muted">Saving...</p>
            </div>
          )}
        </div>
      </div>

      {/* Quantity picker modal */}
      {editingIdx !== null && (
        <QuantityPicker
          value={items[editingIdx].quantity}
          onChange={(val) => handleQuantityChange(editingIdx, val)}
          onClose={() => setEditingIdx(null)}
        />
      )}
    </div>
  )
}

