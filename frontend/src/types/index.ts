export interface Ingredient {
  ingredient: string
  quantity: number
  unit: string
}

export interface NutritionItem {
  ingredient_name: string
  quantity: number
  unit: string
  calories: number
  protein: number
  carbs: number
  fat: number
  source: string
}

export interface MealLogItem {
  id: number
  ingredient_name: string
  quantity: number
  unit: string
  calories: number
  protein: number
  carbs: number
  fat: number
  source: string
}

export interface MealLog {
  id: number
  date: string
  meal_slot: string
  transcription: string | null
  created_at: string
  items: MealLogItem[]
}

export interface DayMeals {
  date: string
  meals: MealLog[]
  total_calories: number
}

export interface DaySummary {
  date: string
  total_calories: number
  meals: MealLog[]
}

export interface HistoryResponse {
  days: DaySummary[]
  has_more: boolean
}

export type MealSlot = 'breakfast' | 'lunch' | 'dinner' | 'snacks'
