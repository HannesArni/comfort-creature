import { useState, useRef, useEffect, useCallback } from 'react'
import { colors } from '../constants/colors'

interface JoystickProps {
  onMove: (leftSpeed: number, rightSpeed: number) => void
  onStop: () => void
  disabled?: boolean
}

export function Joystick({ onMove, onStop, disabled = false }: JoystickProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 }) // -1 to 1 range
  const [isActive, setIsActive] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const intervalRef = useRef<number | null>(null)
  const lastSentSpeedsRef = useRef({ left: 0, right: 0 })
  const positionRef = useRef({ x: 0, y: 0 }) // For interval to access latest position

  // Convert joystick position to motor speeds
  const calculateMotorSpeeds = (
    x: number,
    y: number
  ): { left: number; right: number } => {
    // y: forward/backward (-1 to 1, where 1 is forward)
    // x: left/right (-1 to 1, where -1 is left)

    // Base speed from forward/backward (40-160 range)
    const baseSpeed = y * 60

    const turnAmount = x * (0.8 * (60 - Math.abs(baseSpeed)))

    // Differential drive: add turn to one side, subtract from other
    const leftSpeed = baseSpeed + turnAmount
    const rightSpeed = baseSpeed - turnAmount

    // Map to 40-160 range (only positive speeds for forward)
    const mapToMotorRange = (speed: number): number => {
      if (Math.abs(speed) < 10) return 0 // Deadzone
      if (speed > 0) {
        return Math.min(100, Math.max(0, speed))
      }
      return 0 // No reverse for now
    }

    return {
      left: Math.round(mapToMotorRange(leftSpeed)),
      right: Math.round(mapToMotorRange(rightSpeed)),
    }
  }

  const handleStart = (clientX: number, clientY: number) => {
    if (disabled) return
    setIsActive(true)
    updatePosition(clientX, clientY)

    // Start interval to send commands (reduced frequency for less TCP overhead)
    intervalRef.current = window.setInterval(() => {
      const pos = positionRef.current
      const speeds = calculateMotorSpeeds(pos.x, pos.y)
      // Send if speeds changed at all
      const lastSpeeds = lastSentSpeedsRef.current
      if (speeds.left !== lastSpeeds.left || speeds.right !== lastSpeeds.right) {
        onMove(speeds.left, speeds.right)
        lastSentSpeedsRef.current = speeds
      }
    }, 200)
  }

  const handleMove = (clientX: number, clientY: number) => {
    if (!isActive) return
    updatePosition(clientX, clientY)
  }

  const handleEnd = () => {
    setIsActive(false)
    setPosition({ x: 0, y: 0 })
    positionRef.current = { x: 0, y: 0 }

    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    lastSentSpeedsRef.current = { left: 0, right: 0 }
    onStop()
  }

  const updatePosition = (clientX: number, clientY: number) => {
    if (!containerRef.current) return

    const rect = containerRef.current.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2

    // Calculate position relative to center
    const maxRadius = Math.min(rect.width, rect.height) / 2 - 40
    let dx = clientX - centerX
    let dy = centerY - clientY // Invert Y so up is positive

    // Constrain to circle
    const distance = Math.sqrt(dx * dx + dy * dy)
    if (distance > maxRadius) {
      dx = (dx / distance) * maxRadius
      dy = (dy / distance) * maxRadius
    }

    // Normalize to -1 to 1 range
    const x = dx / maxRadius
    const y = dy / maxRadius

    // Update both state (for rendering) and ref (for interval)
    const newPosition = { x, y }
    setPosition(newPosition)
    positionRef.current = newPosition
    // Don't send immediately - let the interval handle it to reduce message frequency
  }

  // Touch handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault()
    const touch = e.touches[0]
    handleStart(touch.clientX, touch.clientY)
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    e.preventDefault()
    const touch = e.touches[0]
    handleMove(touch.clientX, touch.clientY)
  }

  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault()
    handleEnd()
  }

  // Mouse handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    handleStart(e.clientX, e.clientY)
  }

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      handleMove(e.clientX, e.clientY)
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [isActive]
  )

  const handleMouseUp = useCallback(() => {
    handleEnd()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (isActive) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isActive, handleMouseMove, handleMouseUp])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  const speeds = calculateMotorSpeeds(position.x, position.y)
  const maxRadius = containerRef.current
    ? Math.min(containerRef.current.clientWidth, containerRef.current.clientHeight) /
        2 -
      100
    : 200

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        userSelect: 'none',
      }}
    >
      {/* Joystick area */}
      <div
        ref={containerRef}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onTouchCancel={handleTouchEnd}
        onMouseDown={handleMouseDown}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: colors.SURFACE,
          cursor: disabled ? 'not-allowed' : 'pointer',
          touchAction: 'none',
          opacity: disabled ? 0.5 : 1,
        }}
      >
        {/* Center crosshair */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: '6px',
            height: '80px',
            background: colors.GRID,
            transform: 'translate(-50%, -50%)',
            borderRadius: '3px',
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: '80px',
            height: '6px',
            background: colors.GRID,
            transform: 'translate(-50%, -50%)',
            borderRadius: '3px',
          }}
        />

        {/* Joystick handle */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: '120px',
            height: '120px',
            borderRadius: '50%',
            background: isActive
              ? `linear-gradient(135deg, ${colors.SUCCESS}, #00cc88)`
              : `linear-gradient(135deg, ${colors.PRIMARY}, ${colors.SECONDARY})`,
            border: `4px solid ${colors.TEXT_PRIMARY}`,
            transform: `translate(calc(-50% + ${position.x * maxRadius}px), calc(-50% - ${position.y * maxRadius}px))`,
            boxShadow: isActive
              ? '0 0 40px rgba(0, 255, 136, 0.8)'
              : '0 6px 20px rgba(0, 0, 0, 0.5)',
            transition: isActive ? 'none' : 'all 0.3s ease',
          }}
        />
      </div>

      {/* Motor speed display */}
      <div
        style={{
          position: 'absolute',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '40px',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px 40px',
          background: colors.SURFACE,
          borderRadius: '16px',
          border: `2px solid ${colors.GRID}`,
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
          zIndex: 10,
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              fontSize: '14px',
              color: colors.TEXT_SECONDARY,
              marginBottom: '8px',
            }}
          >
            LEFT MOTOR
          </div>
          <div
            style={{
              fontSize: '48px',
              fontWeight: 700,
              color: speeds.left > 0 ? colors.SUCCESS : colors.TEXT_SECONDARY,
              fontFamily: 'monospace',
            }}
          >
            {speeds.left}
          </div>
        </div>

        <div
          style={{
            width: '2px',
            height: '60px',
            background: colors.GRID,
          }}
        />

        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              fontSize: '14px',
              color: colors.TEXT_SECONDARY,
              marginBottom: '8px',
            }}
          >
            RIGHT MOTOR
          </div>
          <div
            style={{
              fontSize: '48px',
              fontWeight: 700,
              color: speeds.right > 0 ? colors.SUCCESS : colors.TEXT_SECONDARY,
              fontFamily: 'monospace',
            }}
          >
            {speeds.right}
          </div>
        </div>
      </div>
    </div>
  )
}
