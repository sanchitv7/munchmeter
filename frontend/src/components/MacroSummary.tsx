interface MacroSummaryProps {
  calories: number
  protein?: number
  carbs?: number
  fat?: number
  size?: 'sm' | 'lg'
}

export function MacroSummary({ calories, protein, carbs, fat, size = 'lg' }: MacroSummaryProps) {
  const isLarge = size === 'lg'

  return (
    <div className="flex items-center gap-4 flex-wrap">
      <div>
        <span className={`font-bold ${isLarge ? 'text-3xl' : 'text-lg'} text-text`}>
          {Math.round(calories)}
        </span>
        <span className={`text-muted ${isLarge ? 'text-sm' : 'text-xs'} ml-1`}>cal</span>
      </div>
      {(protein !== undefined || carbs !== undefined || fat !== undefined) && (
        <div className="flex items-center gap-3">
          {protein !== undefined && (
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-accent" />
              <span className={`text-muted ${isLarge ? 'text-sm' : 'text-xs'}`}>{Math.round(protein)}g P</span>
            </div>
          )}
          {carbs !== undefined && (
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <span className={`text-muted ${isLarge ? 'text-sm' : 'text-xs'}`}>{Math.round(carbs)}g C</span>
            </div>
          )}
          {fat !== undefined && (
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-success" />
              <span className={`text-muted ${isLarge ? 'text-sm' : 'text-xs'}`}>{Math.round(fat)}g F</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
