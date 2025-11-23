import { useEffect, useRef } from 'react'
import { useRobotWebSocket } from '../hooks/useRobotWebSocket'
import { Joystick } from '../components/Joystick'
import { AutomaticModeToggle } from '../components/AutomaticModeToggle'
import { colors } from '../constants/colors'

export function RemoteControl() {
  const { isConnected, robotState, sendMotor, stopMotors } = useRobotWebSocket()
  const lastMotorSpeedsRef = useRef({ left: 0, right: 0 })

  const handleJoystickMove = (leftSpeed: number, rightSpeed: number) => {
    lastMotorSpeedsRef.current = { left: leftSpeed, right: rightSpeed }
    sendMotor('both', 0, leftSpeed, rightSpeed)
  }

  const handleJoystickStop = () => {
    lastMotorSpeedsRef.current = { left: 0, right: 0 }
    stopMotors()
  }

  // Keep-alive: Send motor commands periodically in manual mode to prevent Arduino timeout
  useEffect(() => {
    if (!isConnected || robotState?.in_automatic_mode) {
      return
    }

    const interval = setInterval(() => {
      // Resend last motor speeds to keep Arduino alive
      const { left, right } = lastMotorSpeedsRef.current
      sendMotor('both', 0, left, right)
    }, 500) // Send every 500ms

    return () => clearInterval(interval)
  }, [isConnected, robotState?.in_automatic_mode, sendMotor])

  return (
    <div
      style={{
        width: '100vw',
        height: '100vh',
        background: colors.BACKGROUND,
        userSelect: 'none',
        overflow: 'hidden',
        position: 'fixed',
        top: 0,
        left: 0,
        margin: 0,
        padding: 0,
      }}
    >
      <div
        style={{
          position: 'fixed',
          top: '80px',
          right: '20px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: '8px',
          zIndex: 1002,
        }}
      >
        {/* Connection status */}
        <div
          style={{
            padding: '8px 16px',
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            borderRadius: 8,
            fontSize: 14,
            backdropFilter: 'blur(10px)',
            border: `2px solid ${isConnected ? colors.SUCCESS : colors.ERROR}`,
          }}
        >
          <span style={{ color: isConnected ? colors.SUCCESS : colors.ERROR }}>●</span>{' '}
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>

        {/* Automatic mode toggle */}
        <AutomaticModeToggle />
      </div>
      <Joystick
        onMove={handleJoystickMove}
        onStop={handleJoystickStop}
        disabled={!isConnected}
      />
    </div>
  )
}
