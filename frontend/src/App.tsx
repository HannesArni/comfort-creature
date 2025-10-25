import { Layer, Image, Circle, Text } from 'react-konva'
import './App.css'
import { ZoomableCanvas } from './components/ZoomableCanvas'
import { Grid } from './components/Grid'
import { useRobotWebSocket } from './hooks/useRobotWebSocket'
import useImage from 'use-image'

// Note: Canvas uses Y-down, Robot uses Y-up
// We negate Y coordinates when rendering to flip the axis

function App() {
  const [image] = useImage('/public/chat-gpt-chair.png')
  const { robotState, isConnected, error, sendTarget, sendStart } = useRobotWebSocket()

  const handleCanvasClick = (worldX: number, worldY: number) => {
    console.log(`Setting target to (${worldX.toFixed(2)}, ${worldY.toFixed(2)})`)
    sendTarget(worldX, worldY)
    sendStart()
  }

  return (
    <>
      {/* Connection status indicator */}
      <div
        style={{
          position: 'fixed',
          top: 10,
          right: 10,
          padding: '8px 16px',
          background: isConnected ? '#4caf50' : '#f44336',
          color: 'white',
          borderRadius: 4,
          fontSize: 14,
          zIndex: 1000,
        }}
      >
        {isConnected ? '● Connected' : '● Disconnected'}
        {error && <div style={{ fontSize: 12 }}>{error}</div>}
      </div>

      <ZoomableCanvas onCanvasClick={handleCanvasClick}>
        {(scale, position) => (
          <>
            <Layer>
              <Grid
                scale={scale}
                position={position}
                dimensions={{
                  width: window.innerWidth,
                  height: window.innerHeight,
                }}
              />
            </Layer>

            <Layer>
              {/* Robot/Chair - position from WebSocket or default */}
              {robotState?.pose && (
                <>
                  {/* Debug: Heading text */}
                  <Text
                    x={robotState.pose.position.x}
                    y={-robotState.pose.position.y - 80}
                    text={`Heading: ${robotState.pose.heading.toFixed(2)} rad (${((robotState.pose.heading * 180) / Math.PI).toFixed(0)}°)`}
                    fontSize={14 / scale}
                    fill="white"
                    stroke="black"
                    strokeWidth={1 / scale}
                  />
                  <Image
                    image={image}
                    x={robotState.pose.position.x}
                    y={-robotState.pose.position.y}
                    width={80}
                    height={100}
                    offsetX={40}
                    offsetY={50}
                    rotation={-robotState.pose.heading * (180 / Math.PI) + 180}
                  />
                </>
              )}
              {!robotState?.pose && (
                <Image
                  image={image}
                  x={0}
                  y={0}
                  width={80}
                  height={100}
                  offsetX={40}
                  offsetY={50}
                  rotation={0}
                />
              )}

              {/* Target position if set */}
              {robotState?.target && (
                <>
                  <Circle
                    x={robotState.target.x}
                    y={-robotState.target.y}
                    radius={10 / scale}
                    stroke="green"
                    strokeWidth={2 / scale}
                  />
                  <Text
                    x={robotState.target.x}
                    y={-robotState.target.y - 20 / scale}
                    text={`Target (${robotState.target.x.toFixed(2)}, ${robotState.target.y.toFixed(2)})`}
                    fontSize={12 / scale}
                    fill="green"
                  />
                </>
              )}

              {/* Obstacles if any */}
              {robotState?.obstacles?.map((obstacle, i) => (
                <Circle
                  key={`obstacle-${i}`}
                  x={obstacle.x}
                  y={-obstacle.y}
                  radius={5 / scale}
                  fill="red"
                  opacity={0.6}
                />
              ))}
            </Layer>
          </>
        )}
      </ZoomableCanvas>
    </>
  )
}

export default App
