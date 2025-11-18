import { useState, useRef, useEffect } from 'react'
import { colors } from '../constants/colors'

interface MotorSliderProps {
  label: string
  currentSpeed: number
  onSpeedChange: (speed: number) => void
  onStop: () => void
  disabled?: boolean
}

export function MotorSlider({
  label,
  currentSpeed,
  onSpeedChange,
  onStop,
  disabled = false,
}: MotorSliderProps) {
  const [sliderValue, setSliderValue] = useState(105) // Midpoint of 50-160
  const [isActive, setIsActive] = useState(false)
  const intervalRef = useRef<number | null>(null)

  const startMotor = () => {
    if (disabled) return
    setIsActive(true)

    // Send initial command
    onSpeedChange(sliderValue)

    // Start interval to send commands every 100ms (deadman switch pattern)
    intervalRef.current = window.setInterval(() => {
      onSpeedChange(sliderValue)
    }, 100)
  }

  const stopMotor = () => {
    setIsActive(false)

    // Clear interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // Send stop command
    onStop()
  }

  // Update the speed being sent when slider value changes while active
  useEffect(() => {
    if (isActive && intervalRef.current) {
      // The interval will pick up the new sliderValue on next iteration
    }
  }, [sliderValue, isActive])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  // Handle touch/mouse events
  const handleButtonStart = (e: React.TouchEvent | React.MouseEvent) => {
    e.preventDefault()
    startMotor()
  }

  const handleButtonEnd = (e: React.TouchEvent | React.MouseEvent) => {
    e.preventDefault()
    stopMotor()
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '16px',
        padding: '20px',
        background: colors.SURFACE,
        borderRadius: '12px',
        border: `2px solid ${isActive ? colors.SUCCESS : colors.GRID}`,
        minWidth: '140px',
      }}
    >
      {/* Label */}
      <div
        style={{
          fontSize: '18px',
          fontWeight: 600,
          color: colors.TEXT_PRIMARY,
        }}
      >
        {label}
      </div>

      {/* Hold button */}
      <button
        onTouchStart={handleButtonStart}
        onTouchEnd={handleButtonEnd}
        onTouchCancel={handleButtonEnd}
        onMouseDown={handleButtonStart}
        onMouseUp={handleButtonEnd}
        onMouseLeave={handleButtonEnd}
        disabled={disabled}
        style={{
          width: '100px',
          height: '100px',
          borderRadius: '50%',
          border: 'none',
          background: isActive
            ? `linear-gradient(135deg, ${colors.SUCCESS}, #00cc88)`
            : `linear-gradient(135deg, ${colors.PRIMARY}, ${colors.SECONDARY})`,
          color: colors.TEXT_PRIMARY,
          fontSize: '16px',
          fontWeight: 600,
          cursor: disabled ? 'not-allowed' : 'pointer',
          touchAction: 'none',
          userSelect: 'none',
          boxShadow: isActive
            ? '0 0 20px rgba(0, 255, 136, 0.5)'
            : '0 4px 8px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.2s ease',
          opacity: disabled ? 0.5 : 1,
        }}
      >
        {isActive ? 'RUNNING' : 'HOLD TO START'}
      </button>

      {/* Vertical slider */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <span style={{ fontSize: '14px', color: colors.TEXT_SECONDARY }}>Speed</span>
        <input
          type="range"
          min="50"
          max="160"
          value={sliderValue}
          onChange={(e) => setSliderValue(Number(e.target.value))}
          disabled={disabled}
          style={{
            width: '200px',
            height: '8px',
            WebkitAppearance: 'none',
            appearance: 'none',
            background: `linear-gradient(to right, ${colors.PRIMARY} 0%, ${colors.SUCCESS} 100%)`,
            outline: 'none',
            borderRadius: '4px',
            opacity: disabled ? 0.5 : 1,
          }}
        />
        <span
          style={{
            fontSize: '24px',
            fontWeight: 600,
            color: isActive ? colors.SUCCESS : colors.TEXT_PRIMARY,
            minWidth: '60px',
            textAlign: 'center',
          }}
        >
          {sliderValue}
        </span>
      </div>

      {/* Current motor speed from server */}
      <div
        style={{
          fontSize: '12px',
          color: colors.TEXT_SECONDARY,
          textAlign: 'center',
        }}
      >
        Actual: {currentSpeed}
      </div>
    </div>
  )
}
