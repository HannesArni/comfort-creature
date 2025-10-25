import { Group, Image, Circle, Line } from 'react-konva'
import type { GlobalPose, UltrasonicSensor } from '../types/generated'
import { colors } from '../constants/colors'

interface RobotLocalFrameProps {
  pose: GlobalPose
  image?: HTMLImageElement
  sensors?: UltrasonicSensor[]
}
const ULTRASONIC_SENSOR_RANGE = 400

/**
 * RobotLocalFrame - A coordinate system group centered on the robot
 *
 * This component creates a Konva Group positioned at the robot's location
 * and rotated to match its heading. All children are positioned in the
 * robot's local coordinate frame:
 * - (0, 0) is the robot center
 * - Positive X is right relative to robot
 * - Negative Y is forward (canvas Y-down, robot Y-up)
 */
export function RobotLocalFrame({ pose, image, sensors }: RobotLocalFrameProps) {
  return (
    <Group
      x={pose.position.x}
      y={-pose.position.y}
      rotation={-pose.heading * (180 / Math.PI)}
    >
      {/* Chair image at origin of local frame */}
      <Image
        image={image}
        x={0}
        y={0}
        width={80}
        height={100}
        offsetX={40}
        offsetY={50}
        rotation={180} // Base rotation to orient chair forward
      />

      {/* Render actual sensors from robot */}
      {sensors?.map((sensor, i) => (
        <Group key={i}>
          {/* Sensor position */}
          <Circle
            x={sensor.pose.position.x}
            y={-sensor.pose.position.y}
            radius={2}
            fill={colors.SENSOR_RANGE}
            opacity={0.7}
          />

          {/* Sensor heading indicator (line showing direction) */}
          <Line
            points={[
              sensor.pose.position.x,
              -sensor.pose.position.y,
              sensor.pose.position.x +
                ULTRASONIC_SENSOR_RANGE * Math.sin(sensor.pose.heading),
              -(
                sensor.pose.position.y +
                ULTRASONIC_SENSOR_RANGE * Math.cos(sensor.pose.heading)
              ),
            ]}
            stroke={colors.SENSOR_RANGE}
            strokeWidth={0.7}
            opacity={1}
          />
        </Group>
      ))}
    </Group>
  )
}
