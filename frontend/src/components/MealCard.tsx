import { useState } from 'react'
import type { MealLog } from '../types'

const SLOT_ICONS: Record<string, string> = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙',
  snacks: '🍿',
}

interface MealCardProps {
  meal: MealLog
  defaultExpanded?: boolean
}

export function MealCard({ meal, defaultExpanded = false }: MealCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded)

  const totalCalories = Math.round(meal.items.reduce((sum, i) => sum + i.calories, 0))
  const ingredientNames = meal.items.map(i => i.ingredient_name).join(', ')

  return (
    <div
      className="bg-surface rounded-card shadow-card p-4 cursor-pointer active:scale-[0.99] transition-transform"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{SLOT_ICONS[meal.meal_slot] || '🍽️'}</span>
          <div>
            <h3 className="font-semibold text-text capitalize">{meal.meal_slot}</h3>
            <p className="text-sm text-muted truncate max-w-[200px]">{ingredientNames}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="font-bold text-text">{totalCalories}</span>
          <span className="text-xs text-muted ml-1">cal</span>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100 space-y-2">
          {meal.items.map((item) => (
            <div key={item.id} className="flex items-center justify-between text-sm">
              <div>
                <span className="text-text">{item.ingredient_name}</span>
                <span className="text-muted ml-2">{item.quantity} {item.unit}</span>
              </div>
              <div className="flex items-center gap-3 text-muted text-xs">
                <span>{Math.round(item.calories)} cal</span>
                <span className="text-accent">{Math.round(item.protein)}P</span>
                <span className="text-secondary">{Math.round(item.carbs)}C</span>
                <span className="text-success">{Math.round(item.fat)}F</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
