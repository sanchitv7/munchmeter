import type { MealSlot } from '../types'

const SLOTS: { value: MealSlot; label: string }[] = [
  { value: 'breakfast', label: 'Breakfast' },
  { value: 'lunch', label: 'Lunch' },
  { value: 'dinner', label: 'Dinner' },
  { value: 'snacks', label: 'Snacks' },
]

interface MealSlotPickerProps {
  selected: MealSlot | null
  onChange: (slot: MealSlot) => void
}

export function MealSlotPicker({ selected, onChange }: MealSlotPickerProps) {
  return (
    <div className="flex gap-2">
      {SLOTS.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onChange(value)}
          className={`px-4 py-2 rounded-pill text-sm font-medium transition-colors ${
            selected === value
              ? 'bg-accent text-white'
              : 'bg-gray-100 text-muted hover:bg-gray-200'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
