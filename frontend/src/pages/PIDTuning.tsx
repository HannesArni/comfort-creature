import { useRobotWebSocket } from '../hooks/useRobotWebSocket'
import { colors } from '../constants/colors'
import { useMemo, memo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { PIDState } from '../types/generated'

interface ChartData {
  timestamp: number
  [key: string]: number
}

function transformPIDData(data: PIDState[]): ChartData[] {
  return data.map((state) => ({
    timestamp: state.timestamp,
    target: state.target_velocity,
    actual: state.actual_velocity,
    error: state.error,
    p: state.p_term,
    d: state.d_term,
    i: state.i_term,
    input: state.motor_input,
  }))
}

interface MotorChartsProps {
  motorName: string
  data: PIDState[]
}

const MotorCharts = memo(({ motorName, data }: MotorChartsProps) => {
  // Memoize data transformation to avoid recalculating on every render
  const relativeData = useMemo(() => {
    const chartData = transformPIDData(data)

    if (chartData.length === 0) {
      return []
    }

    // Downsample if we have too many points (keep every 2nd point if > 250)
    const downsampledData =
      chartData.length > 250
        ? chartData.filter((_, index) => index % 2 === 0)
        : chartData

    // Calculate time relative to most recent sample (0 = now, negative = past)
    const endTime = downsampledData[downsampledData.length - 1]?.timestamp || 0
    return downsampledData.map((d) => ({
      ...d,
      time: d.timestamp - endTime, // Most recent = 0, older = negative
    }))
  }, [data])

  if (relativeData.length === 0) {
    return (
      <div style={{ padding: '20px', color: colors.TEXT_SECONDARY }}>
        No data available yet. Waiting for motor controller...
      </div>
    )
  }

  return (
    <div style={{ marginBottom: '40px' }}>
      <h2 style={{ color: colors.TEXT_PRIMARY, marginBottom: '20px' }}>
        {motorName} Motor
      </h2>

      {/* Velocity Chart */}
      <div style={{ marginBottom: '30px' }}>
        <h3
          style={{
            color: colors.TEXT_SECONDARY,
            fontSize: '16px',
            marginBottom: '10px',
          }}
        >
          Velocity (cm/s)
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={relativeData}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.GRID_MINOR} />
            <XAxis
              dataKey="time"
              stroke={colors.TEXT_SECONDARY}
              label={{ value: 'Time (s)', position: 'insideBottom', offset: -5 }}
              tickFormatter={(value) => value.toFixed(1)}
            />
            <YAxis stroke={colors.TEXT_SECONDARY} />
            <Tooltip
              contentStyle={{
                background: colors.SURFACE,
                border: `1px solid ${colors.BORDER}`,
                borderRadius: '4px',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="target"
              stroke={colors.TARGET}
              dot={false}
              name="Target"
              strokeWidth={2}
              isAnimationActive={false}
              connectNulls={true}
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke={colors.SUCCESS}
              dot={false}
              name="Actual"
              strokeWidth={2}
              isAnimationActive={false}
              connectNulls={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Error Chart */}
      <div style={{ marginBottom: '30px' }}>
        <h3
          style={{
            color: colors.TEXT_SECONDARY,
            fontSize: '16px',
            marginBottom: '10px',
          }}
        >
          Velocity Error (cm/s)
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={relativeData}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.GRID_MINOR} />
            <XAxis
              dataKey="time"
              stroke={colors.TEXT_SECONDARY}
              label={{ value: 'Time (s)', position: 'insideBottom', offset: -5 }}
              tickFormatter={(value) => value.toFixed(1)}
            />
            <YAxis stroke={colors.TEXT_SECONDARY} />
            <Tooltip
              contentStyle={{
                background: colors.SURFACE,
                border: `1px solid ${colors.BORDER}`,
                borderRadius: '4px',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="error"
              stroke={colors.ERROR}
              dot={false}
              name="Error"
              strokeWidth={2}
              isAnimationActive={false}
              connectNulls={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* PID Terms Chart */}
      <div style={{ marginBottom: '30px' }}>
        <h3
          style={{
            color: colors.TEXT_SECONDARY,
            fontSize: '16px',
            marginBottom: '10px',
          }}
        >
          PID Terms
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={relativeData}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.GRID_MINOR} />
            <XAxis
              dataKey="time"
              stroke={colors.TEXT_SECONDARY}
              label={{ value: 'Time (s)', position: 'insideBottom', offset: -5 }}
              tickFormatter={(value) => value.toFixed(1)}
            />
            <YAxis stroke={colors.TEXT_SECONDARY} />
            <Tooltip
              contentStyle={{
                background: colors.SURFACE,
                border: `1px solid ${colors.BORDER}`,
                borderRadius: '4px',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="p"
              stroke="#8884d8"
              dot={false}
              name="P term"
              strokeWidth={2}
              isAnimationActive={false}
              connectNulls={true}
            />
            <Line
              type="monotone"
              dataKey="d"
              stroke="#82ca9d"
              dot={false}
              name="D term"
              strokeWidth={2}
              isAnimationActive={false}
              connectNulls={true}
            />
            <Line
              type="monotone"
              dataKey="i"
              stroke="#ffc658"
              dot={false}
              name="I term"
              strokeWidth={2}
              isAnimationActive={false}
              connectNulls={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Motor Input Chart */}
      <div style={{ marginBottom: '30px' }}>
        <h3
          style={{
            color: colors.TEXT_SECONDARY,
            fontSize: '16px',
            marginBottom: '10px',
          }}
        >
          Motor Input (0-100)
        </h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={relativeData}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.GRID_MINOR} />
            <XAxis
              dataKey="time"
              stroke={colors.TEXT_SECONDARY}
              label={{ value: 'Time (s)', position: 'insideBottom', offset: -5 }}
              tickFormatter={(value) => value.toFixed(1)}
            />
            <YAxis stroke={colors.TEXT_SECONDARY} />
            <Tooltip
              contentStyle={{
                background: colors.SURFACE,
                border: `1px solid ${colors.BORDER}`,
                borderRadius: '4px',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="input"
              stroke={colors.ROBOT}
              dot={false}
              name="Motor Input"
              strokeWidth={2}
              isAnimationActive={false}
              connectNulls={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
})

MotorCharts.displayName = 'MotorCharts'

export function PIDTuning() {
  const { pidHistory, isConnected, error } = useRobotWebSocket()

  return (
    <div
      style={{
        padding: '20px',
        maxWidth: '1400px',
        margin: '0 auto',
        minHeight: '100vh',
        background: colors.BACKGROUND,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px',
        }}
      >
        <h1 style={{ color: colors.TEXT_PRIMARY, margin: 0 }}>PID Controller Tuning</h1>
        <div
          style={{
            padding: '8px 16px',
            background: colors.SURFACE,
            color: colors.TEXT_PRIMARY,
            borderRadius: 8,
            fontSize: 14,
            border: `2px solid ${isConnected ? colors.SUCCESS : colors.ERROR}`,
          }}
        >
          <span style={{ color: isConnected ? colors.SUCCESS : colors.ERROR }}>●</span>{' '}
          {isConnected ? 'Connected' : 'Disconnected'}
          {error && <div style={{ fontSize: 12, color: colors.ERROR }}>{error}</div>}
        </div>
      </div>

      {/* Info */}
      <div
        style={{
          padding: '12px 16px',
          background: colors.SURFACE,
          borderRadius: 8,
          marginBottom: '30px',
          color: colors.TEXT_SECONDARY,
          fontSize: 14,
        }}
      >
        <p style={{ margin: 0 }}>
          Real-time visualization of PID controller performance. Charts update at 10 Hz.
          Showing last {pidHistory.left.length} samples (~
          {(pidHistory.left.length / 10).toFixed(1)}s of data).
        </p>
      </div>

      {/* Charts */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(600px, 1fr))',
          gap: '40px',
        }}
      >
        <MotorCharts motorName="Left" data={pidHistory.left} />
        <MotorCharts motorName="Right" data={pidHistory.right} />
      </div>
    </div>
  )
}
