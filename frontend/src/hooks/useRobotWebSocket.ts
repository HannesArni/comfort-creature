import { useState, useEffect, useRef, useCallback } from 'react'
import type { UltrasonicSensor, PIDState } from '../types/generated'

interface RobotState {
  pose: {
    position: {
      x: number
      y: number
    }
    heading: number
  }
  obstacles?: Array<{ x: number; y: number }>
  target?: { x: number; y: number }
  sensors?: Array<UltrasonicSensor>
  motor_speeds?: { left: number; right: number }
  pid_data?: {
    left: PIDState
    right: PIDState
  } | null
  in_automatic_mode?: boolean
}

interface PIDHistory {
  left: PIDState[]
  right: PIDState[]
}

interface UseRobotWebSocketResult {
  robotState: RobotState | null
  isConnected: boolean
  error: string | null
  pidHistory: PIDHistory
  sendTarget: (x: number, y: number) => void
  sendStart: () => void
  sendStop: () => void
  sendMotor: (
    motor: 'left' | 'right' | 'both',
    speed: number,
    leftSpeed?: number,
    rightSpeed?: number
  ) => void
  stopMotors: () => void
  sendAutomaticMode: (enabled: boolean) => void
}

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
const RECONNECT_DELAY = 1_000
const MAX_PID_HISTORY = 100 // Store up to 100 samples (10 seconds at 10Hz)

export function useRobotWebSocket(): UseRobotWebSocketResult {
  const [robotState, setRobotState] = useState<RobotState | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pidHistory, setPidHistory] = useState<PIDHistory>({ left: [], right: [] })
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          if (message.type === 'state_update') {
            setRobotState(message.data)

            // Update PID history if new PID data is available
            if (message.data.pid_data) {
              setPidHistory((prev) => ({
                left: [...prev.left, message.data.pid_data.left].slice(
                  -MAX_PID_HISTORY
                ),
                right: [...prev.right, message.data.pid_data.right].slice(
                  -MAX_PID_HISTORY
                ),
              }))
            }
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError('WebSocket connection error')
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        wsRef.current = null

        // Attempt to reconnect
        reconnectTimeoutRef.current = window.setTimeout(() => {
          console.log('Attempting to reconnect...')
          connect()
        }, RECONNECT_DELAY)
      }

      wsRef.current = ws
    } catch (err) {
      console.error('Failed to create WebSocket:', err)
      setError('Failed to create WebSocket connection')
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  const sendMessage = useCallback((message: object) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [])

  const sendTarget = useCallback(
    (x: number, y: number) => {
      sendMessage({
        type: 'set_target',
        data: { x, y },
      })
    },
    [sendMessage]
  )

  const sendStart = useCallback(() => {
    sendMessage({ type: 'start' })
  }, [sendMessage])

  const sendStop = useCallback(() => {
    sendMessage({ type: 'stop' })
  }, [sendMessage])

  const sendMotor = useCallback(
    (
      motor: 'left' | 'right' | 'both',
      speed: number,
      leftSpeed?: number,
      rightSpeed?: number
    ) => {
      const data: {
        motor: string
        speed: number
        left_speed?: number
        right_speed?: number
      } = {
        motor,
        speed,
      }
      if (motor === 'both' && leftSpeed !== undefined && rightSpeed !== undefined) {
        data.left_speed = leftSpeed
        data.right_speed = rightSpeed
      }
      sendMessage({
        type: 'set_motor',
        data,
      })
    },
    [sendMessage]
  )

  const stopMotors = useCallback(() => {
    sendMessage({ type: 'stop' })
  }, [sendMessage])

  const sendAutomaticMode = useCallback(
    (enabled: boolean) => {
      sendMessage({
        type: 'set_automatic_mode',
        data: { enabled },
      })
    },
    [sendMessage]
  )

  return {
    robotState,
    isConnected,
    error,
    pidHistory,
    sendTarget,
    sendStart,
    sendStop,
    sendMotor,
    stopMotors,
    sendAutomaticMode,
  }
}
