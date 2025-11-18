import { useRobotWebSocket } from '../hooks/useRobotWebSocket'
import { MotorSlider } from '../components/MotorSlider'
import { colors } from '../constants/colors'

export function RemoteControl() {
  const { robotState, isConnected, error, sendMotor, stopMotors } = useRobotWebSocket()

  const handleLeftMotorChange = (speed: number) => {
    sendMotor('left', speed)
  }

  const handleRightMotorChange = (speed: number) => {
    sendMotor('right', speed)
  }

  const handleLeftMotorStop = () => {
    sendMotor('left', 0)
  }

  const handleRightMotorStop = () => {
    sendMotor('right', 0)
  }

  const handleEmergencyStop = () => {
    stopMotors()
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: colors.BACKGROUND,
        padding: '20px',
        gap: '40px',
      }}
    >
      {/* Connection status indicator */}
      <div
        style={{
          position: 'fixed',
          top: 70,
          right: 10,
          padding: '8px 16px',
          background: colors.SURFACE,
          color: colors.TEXT_PRIMARY,
          borderRadius: 8,
          fontSize: 14,
          zIndex: 1000,
          border: `2px solid ${isConnected ? colors.SUCCESS : colors.ERROR}`,
        }}
      >
        <span style={{ color: isConnected ? colors.SUCCESS : colors.ERROR }}>●</span>{' '}
        {isConnected ? 'Connected' : 'Disconnected'}
        {error && <div style={{ fontSize: 12, color: colors.ERROR }}>{error}</div>}
      </div>

      {/* Title */}
      <h1
        style={{
          fontSize: '32px',
          fontWeight: 700,
          color: colors.TEXT_PRIMARY,
          marginTop: '60px',
        }}
      >
        Remote Control
      </h1>

      {/* Motor sliders */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          gap: '40px',
          flexWrap: 'wrap',
          justifyContent: 'center',
        }}
      >
        <MotorSlider
          label="Left Motor"
          currentSpeed={robotState?.motor_speeds?.left ?? 0}
          onSpeedChange={handleLeftMotorChange}
          onStop={handleLeftMotorStop}
          disabled={!isConnected}
        />
        <MotorSlider
          label="Right Motor"
          currentSpeed={robotState?.motor_speeds?.right ?? 0}
          onSpeedChange={handleRightMotorChange}
          onStop={handleRightMotorStop}
          disabled={!isConnected}
        />
      </div>

      {/* Emergency stop button */}
      <button
        onClick={handleEmergencyStop}
        disabled={!isConnected}
        style={{
          width: '200px',
          height: '200px',
          borderRadius: '50%',
          border: 'none',
          background: isConnected
            ? `linear-gradient(135deg, ${colors.ERROR}, #cc0000)`
            : colors.GRID,
          color: colors.TEXT_PRIMARY,
          fontSize: '24px',
          fontWeight: 700,
          cursor: isConnected ? 'pointer' : 'not-allowed',
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.4)',
          transition: 'all 0.2s ease',
          opacity: isConnected ? 1 : 0.5,
        }}
        onMouseDown={(e) => {
          e.currentTarget.style.transform = 'scale(0.95)'
        }}
        onMouseUp={(e) => {
          e.currentTarget.style.transform = 'scale(1)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)'
        }}
      >
        EMERGENCY
        <br />
        STOP
      </button>

      {/* Instructions */}
      <div
        style={{
          maxWidth: '600px',
          padding: '20px',
          background: colors.SURFACE,
          borderRadius: '12px',
          border: `1px solid ${colors.GRID}`,
          color: colors.TEXT_SECONDARY,
          fontSize: '14px',
          lineHeight: '1.6',
        }}
      >
        <h3 style={{ color: colors.TEXT_PRIMARY, marginTop: 0 }}>Instructions</h3>
        <ul style={{ paddingLeft: '20px', margin: 0 }}>
          <li>Adjust each slider to set desired motor speed (50-160)</li>
          <li>
            <strong>Hold the button</strong> to activate the motor at the selected speed
          </li>
          <li>Release the button to stop the motor (deadman switch)</li>
          <li>Use the emergency stop button to immediately stop all motors</li>
          <li>Motors will automatically stop if connection is lost</li>
        </ul>
      </div>
    </div>
  )
}
