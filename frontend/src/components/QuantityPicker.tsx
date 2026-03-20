import { useRef, useEffect, useCallback } from 'react'

const QUANTITIES = [0.25, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10]
const ITEM_HEIGHT = 40

interface QuantityPickerProps {
  value: number
  onChange: (value: number) => void
  onClose: () => void
}

export function QuantityPicker({ value, onChange, onClose }: QuantityPickerProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const idx = QUANTITIES.indexOf(value)
    if (idx >= 0 && scrollRef.current) {
      scrollRef.current.scrollTop = idx * ITEM_HEIGHT
    }
  }, [value])

  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return
    const idx = Math.round(scrollRef.current.scrollTop / ITEM_HEIGHT)
    const clamped = Math.max(0, Math.min(idx, QUANTITIES.length - 1))
    onChange(QUANTITIES[clamped])
  }, [onChange])

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/30" />
      <div
        className="relative bg-surface rounded-t-2xl w-full max-w-sm p-4 pb-8"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="w-10 h-1 bg-gray-300 rounded-full mx-auto mb-4" />
        <p className="text-center text-sm font-medium text-text mb-3">Select Quantity</p>

        <div className="relative h-[120px] overflow-hidden">
          {/* Selection highlight */}
          <div className="absolute top-[40px] left-0 right-0 h-[40px] bg-accent/10 rounded-lg pointer-events-none z-10" />

          <div
            ref={scrollRef}
            onScroll={handleScroll}
            className="h-full overflow-y-auto snap-y snap-mandatory scrollbar-hide"
            style={{ scrollSnapType: 'y mandatory' }}
          >
            {/* Padding to allow first/last items to center */}
            <div style={{ height: ITEM_HEIGHT }} />
            {QUANTITIES.map((q) => (
              <div
                key={q}
                className="h-[40px] flex items-center justify-center snap-center"
                style={{ scrollSnapAlign: 'center' }}
              >
                <span className={`text-lg font-medium ${q === value ? 'text-accent' : 'text-muted'}`}>
                  {q}
                </span>
              </div>
            ))}
            <div style={{ height: ITEM_HEIGHT }} />
          </div>
        </div>

        <button
          onClick={onClose}
          className="mt-4 w-full py-3 bg-accent text-white rounded-pill font-semibold"
        >
          Done
        </button>
      </div>
    </div>
  )
}
