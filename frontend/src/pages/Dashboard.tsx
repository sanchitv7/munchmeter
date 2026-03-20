import { useMeals } from '../hooks/useMeals'
import { MacroSummary } from '../components/MacroSummary'
import { MealCard } from '../components/MealCard'
import type { MealLog } from '../types'

const SLOT_ORDER = ['breakfast', 'lunch', 'dinner', 'snacks']

export function Dashboard({ onRefreshRef }: { onRefreshRef: React.MutableRefObject<(() => void) | null> }) {
  const today = new Date().toISOString().split('T')[0]
  const { data, loading, refresh } = useMeals(today)

  // Expose refresh to parent so RecordingSheet can trigger it
  onRefreshRef.current = refresh

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const meals = data?.meals || []
  const totalCalories = data?.total_calories || 0

  // Compute total macros
  const totalProtein = meals.reduce((sum, m) => sum + m.items.reduce((s, i) => s + i.protein, 0), 0)
  const totalCarbs = meals.reduce((sum, m) => sum + m.items.reduce((s, i) => s + i.carbs, 0), 0)
  const totalFat = meals.reduce((sum, m) => sum + m.items.reduce((s, i) => s + i.fat, 0), 0)

  // Group meals by slot
  const grouped = SLOT_ORDER.reduce<Record<string, MealLog[]>>((acc, slot) => {
    const slotMeals = meals.filter(m => m.meal_slot === slot)
    if (slotMeals.length > 0) acc[slot] = slotMeals
    return acc
  }, {})

  const formatDate = () => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className="px-5 pt-6 pb-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-text">MunchMeter</h1>
        <p className="text-muted text-sm">{formatDate()}</p>
      </div>

      {/* Summary card */}
      <div className="bg-surface rounded-card shadow-card p-5 mb-6">
        <p className="text-sm text-muted mb-2">Today's intake</p>
        <MacroSummary
          calories={totalCalories}
          protein={totalProtein}
          carbs={totalCarbs}
          fat={totalFat}
        />
      </div>

      {/* Meals by slot */}
      {Object.keys(grouped).length > 0 ? (
        <div className="space-y-3">
          {Object.entries(grouped).map(([_slot, slotMeals]) =>
            slotMeals.map(meal => (
              <MealCard key={meal.id} meal={meal} />
            ))
          )}
        </div>
      ) : (
        <div className="text-center py-16">
          <p className="text-4xl mb-3">🎙️</p>
          <p className="text-text font-medium">No meals logged today</p>
          <p className="text-muted text-sm mt-1">Tap the mic button to get started</p>
        </div>
      )}
    </div>
  )
}
