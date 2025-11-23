import { Layer, Image, Circle, Text } from 'react-konva'
import { ZoomableCanvas } from '../components/ZoomableCanvas'
import { Grid } from '../components/Grid'
import { RobotLocalFrame } from '../components/RobotLocalFrame'
import { AutomaticModeToggle } from '../components/AutomaticModeToggle'
import { useRobotWebSocket } from '../hooks/useRobotWebSocket'
import useImage from 'use-image'
import { colors } from '../constants/colors'

// Note: Canvas uses Y-down, Robot uses Y-up
// We negate Y coordinates when rendering to flip the axis

export function Visualization() {
  const [image] = useImage('/chat-gpt-chair.png')
  // const [skipasundImage] = useImage('/skipasund-44-layout.jpeg')
  // const [aranjaImage] = useImage('/aranja-layout.jpeg')
  const [lhiImage] = useImage('/lhi-teikningar.jpg')
  const { robotState, isConnected, error, sendTarget, sendStart } = useRobotWebSocket()

  const handleCanvasClick = (worldX: number, worldY: number) => {
    console.log(`Setting target to (${worldX.toFixed(2)}, ${worldY.toFixed(2)})`)
    sendTarget(worldX, worldY)
    sendStart()
  }

  return (
    <>
      {/* Connection status and controls */}
      <div
        style={{
          position: 'fixed',
          top: 70,
          right: 10,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: '8px',
          zIndex: 1002,
        }}
      >
        {/* Connection status indicator */}
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

        {/* Automatic mode toggle */}
        <AutomaticModeToggle />
      </div>

      <ZoomableCanvas onCanvasClick={handleCanvasClick}>
        {(scale, position) => (
          <>
            {/*<Layer>*/}
            {/*  <Image*/}
            {/*    image={skipasundImage}*/}
            {/*    x={0}*/}
            {/*    y={0}*/}
            {/*    width={1000 * 1.475}*/}
            {/*    height={800 * 1.5}*/}
            {/*    listening={false}*/}
            {/*  />*/}
            {/*</Layer>*/}
            {/*<Layer>*/}
            {/*  <Image*/}
            {/*    image={aranjaImage}*/}
            {/*    x={4275}*/}
            {/*    y={355 + 35}*/}
            {/*    width={10438 * 0.849}*/}
            {/*    height={6970 * 0.849}*/}
            {/*    rotation={180}*/}
            {/*    listening={false}*/}
            {/*    opacity={0.5}*/}
            {/*  />*/}
            {/*</Layer>*/}
            <Layer>
              <Image
                image={lhiImage}
                x={-1140}
                y={-5910 + 101}
                width={1688 * 3.58}
                height={2400 * 3.58}
                rotation={0}
                listening={false}
                opacity={0.5}
              />
            </Layer>
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
              {/* Robot/Chair with local coordinate frame */}
              {robotState?.pose && (
                <>
                  {/* Debug: Heading text */}
                  <Text
                    x={robotState.pose.position.x}
                    y={-(robotState.pose.position.y + 70)}
                    text={`(${Math.round(robotState.pose.position.x)},${Math.round(robotState.pose.position.y + 70)}) Heading: ${robotState.pose.heading.toFixed(2)} rad (${((robotState.pose.heading * 180) / Math.PI).toFixed(0)}°)`}
                    fontSize={14 / scale}
                    fill={colors.TEXT_PRIMARY}
                  />
                  {/* Robot and local frame elements */}
                  <RobotLocalFrame
                    pose={robotState.pose}
                    image={image}
                    sensors={robotState.sensors}
                  />
                </>
              )}

              {/* Target position if set */}
              {robotState?.target && (
                <>
                  <Circle
                    x={robotState.target.x}
                    y={-robotState.target.y}
                    radius={20 / scale}
                    fill={colors.TARGET}
                    strokeWidth={2 / scale}
                  />
                  <Text
                    x={robotState.target.x}
                    y={-robotState.target.y - 40 / scale}
                    text={`Target`}
                    fontSize={12 / scale}
                    fill={colors.TARGET}
                  />
                </>
              )}
            </Layer>
          </>
        )}
      </ZoomableCanvas>
    </>
  )
}
