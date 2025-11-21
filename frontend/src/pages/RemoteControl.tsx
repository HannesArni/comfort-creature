import { useEffect, useRef } from 'react'
import { useRobotWebSocket } from '../hooks/useRobotWebSocket'
import { Joystick } from '../components/Joystick'
import { colors } from '../constants/colors'

export function RemoteControl() {
  const { isConnected, robotState, sendMotor, stopMotors, sendAutomaticMode } =
    useRobotWebSocket()
  const lastMotorSpeedsRef = useRef({ left: 0, right: 0 })

  const handleJoystickMove = (leftSpeed: number, rightSpeed: number) => {
    lastMotorSpeedsRef.current = { left: leftSpeed, right: rightSpeed }
    sendMotor('both', 0, leftSpeed, rightSpeed)
  }

  const handleJoystickStop = () => {
    lastMotorSpeedsRef.current = { left: 0, right: 0 }
    stopMotors()
  }

  const handleAutomaticModeToggle = () => {
    const newMode = !robotState?.in_automatic_mode
    sendAutomaticMode(newMode)
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
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            background: 'rgba(0, 0, 0, 0.7)',
            padding: '12px 16px',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)',
          }}
        >
          <span
            style={{
              color: 'white',
              fontSize: '14px',
              fontWeight: 500,
            }}
          >
            Automatic Mode
          </span>
          <label
            style={{
              position: 'relative',
              display: 'inline-block',
              width: '48px',
              height: '26px',
              cursor: isConnected ? 'pointer' : 'not-allowed',
              opacity: isConnected ? 1 : 0.5,
            }}
          >
            <input
              type="checkbox"
              checked={robotState?.in_automatic_mode ?? false}
              onChange={handleAutomaticModeToggle}
              disabled={!isConnected}
              style={{
                opacity: 0,
                width: 0,
                height: 0,
              }}
            />
            <span
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: robotState?.in_automatic_mode
                  ? colors.SUCCESS
                  : colors.BUTTON_SECONDARY,
                borderRadius: '13px',
                transition: 'background-color 0.2s',
              }}
            >
              <span
                style={{
                  position: 'absolute',
                  content: '',
                  height: '18px',
                  width: '18px',
                  left: robotState?.in_automatic_mode ? '26px' : '4px',
                  bottom: '4px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                  transition: 'left 0.2s',
                }}
              />
            </span>
          </label>
        </div>
      </div>
      <Joystick
        onMove={handleJoystickMove}
        onStop={handleJoystickStop}
        disabled={!isConnected}
      />
    </div>
  )
}
