import { useRobotWebSocket } from '../hooks/useRobotWebSocket'
import { colors } from '../constants/colors'

export function AutomaticModeToggle() {
  const { isConnected, robotState, sendAutomaticMode } = useRobotWebSocket()

  const handleToggle = () => {
    const newMode = !robotState?.in_automatic_mode
    sendAutomaticMode(newMode)
  }

  return (
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
          onChange={handleToggle}
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
  )
}
