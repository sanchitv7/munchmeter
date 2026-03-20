import type { Ingredient, NutritionItem, DayMeals, HistoryResponse, MealLog, MealSlot } from '../types'

const BASE = '/api'

export async function transcribe(audioBlob: Blob): Promise<{ text: string }> {
  const form = new FormData()
  form.append('file', audioBlob, 'recording.webm')
  const res = await fetch(`${BASE}/transcribe`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Transcription failed: ${res.status}`)
  return res.json()
}

export async function extractIngredients(text: string): Promise<{ ingredients: Ingredient[] }> {
  const res = await fetch(`${BASE}/extract-ingredients`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!res.ok) throw new Error(`Extraction failed: ${res.status}`)
  return res.json()
}

export async function nutritionLookup(ingredients: Ingredient[]): Promise<{
  items: NutritionItem[]
  total_calories: number
  total_protein: number
  total_carbs: number
  total_fat: number
}> {
  const res = await fetch(`${BASE}/nutrition-lookup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ingredients }),
  })
  if (!res.ok) throw new Error(`Nutrition lookup failed: ${res.status}`)
  return res.json()
}

export async function saveMeal(data: {
  date: string
  meal_slot: MealSlot
  transcription?: string
  items: NutritionItem[]
}): Promise<MealLog> {
  const res = await fetch(`${BASE}/meals`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error(`Save meal failed: ${res.status}`)
  return res.json()
}

export async function getMeals(date: string): Promise<DayMeals> {
  const res = await fetch(`${BASE}/meals?date=${date}`)
  if (!res.ok) throw new Error(`Fetch meals failed: ${res.status}`)
  return res.json()
}

export async function getHistory(offset = 0, limit = 20): Promise<HistoryResponse> {
  const res = await fetch(`${BASE}/meals/history?offset=${offset}&limit=${limit}`)
  if (!res.ok) throw new Error(`Fetch history failed: ${res.status}`)
  return res.json()
}
