export function SparklesCore({ className, particleDensity = 30 }) {
  const particles = Array.from({ length: particleDensity })
  return (
    <div className={`sparkle-field ${className || ''}`} aria-hidden="true">
      {particles.map((_, i) => (
        <i
          key={i}
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${Math.random() * 3 + 1}px`,
            height: `${Math.random() * 3 + 1}px`,
            animationDelay: `${Math.random() * 3}s`,
            animationDuration: `${Math.random() * 2 + 2}s`,
          }}
        />
      ))}
    </div>
  )
}

export default SparklesCore
