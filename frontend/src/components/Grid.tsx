import { Line, Text } from 'react-konva'
import { GRID_ORIGIN, GRID_MAJOR, GRID_MINOR, GRID_LABEL } from '../constants/colors'

type GetLineStyleProps = { isOrigin: boolean; isMajor: boolean; scale: number }
const getLineStyle = ({ isOrigin, isMajor, scale }: GetLineStyleProps) => {
  return {
    stroke: isOrigin ? GRID_ORIGIN : isMajor ? GRID_MAJOR : GRID_MINOR,
    strokeWidth: isOrigin ? 2 / scale : isMajor ? 1.5 / scale : 0.3 / scale,
  }
}

interface GridProps {
  scale: number
  position: { x: number; y: number }
  dimensions: { width: number; height: number }
}

export function Grid({ scale, position, dimensions }: GridProps) {
  const lines = []
  const labels = []
  const { width, height } = dimensions

  // Calculate appropriate grid spacing based on zoom level
  const targetPixelSpacing = 50
  const worldSpacing = targetPixelSpacing / scale

  // Round to nice numbers (powers of 10 times 1, 2, or 5)
  const magnitude = Math.pow(10, Math.floor(Math.log10(worldSpacing)))
  const normalized = worldSpacing / magnitude
  let niceSpacing
  if (normalized < 1.5) {
    niceSpacing = magnitude
  } else if (normalized < 3.5) {
    niceSpacing = 2 * magnitude
  } else if (normalized < 7.5) {
    niceSpacing = 5 * magnitude
  } else {
    niceSpacing = 10 * magnitude
  }

  // Calculate visible area in world coordinates
  const visibleLeft = -position.x / scale
  const visibleTop = -position.y / scale
  const visibleRight = visibleLeft + width / scale
  const visibleBottom = visibleTop + height / scale

  // Draw primary grid
  const startX = Math.floor(visibleLeft / niceSpacing) * niceSpacing
  const startY = Math.floor(visibleTop / niceSpacing) * niceSpacing

  const fontSize = 12 / scale
  const labelPadding = 5 / scale

  // Vertical lines
  for (let x = startX; x <= visibleRight; x += niceSpacing) {
    const isMajor = Math.abs(x % (niceSpacing * 5)) < 0.001
    const isOrigin = Math.abs(x) < 0.001
    lines.push(
      <Line
        key={`v-${x}`}
        points={[x, visibleTop, x, visibleBottom]}
        {...getLineStyle({ isOrigin, isMajor, scale })}
      />
    )

    // Add label at top for major lines
    if (isMajor) {
      labels.push(
        <Text
          key={`label-x-${x}`}
          x={x}
          y={visibleTop + labelPadding}
          text={x.toString()}
          fontSize={fontSize}
          fill={GRID_LABEL}
          align="center"
          offsetX={fontSize * 1.5}
        />
      )
    }
  }

  // Horizontal lines
  for (let y = startY; y <= visibleBottom; y += niceSpacing) {
    const isMajor = Math.abs(y % (niceSpacing * 5)) < 0.001
    const isOrigin = Math.abs(y) < 0.001
    lines.push(
      <Line
        key={`h-${y}`}
        points={[visibleLeft, y, visibleRight, y]}
        {...getLineStyle({ isOrigin, isMajor, scale })}
      />
    )

    // Add label on left for major lines
    if (isMajor) {
      labels.push(
        <Text
          key={`label-y-${y}`}
          x={visibleLeft + labelPadding}
          y={y}
          text={y.toString()}
          fontSize={fontSize}
          fill={GRID_LABEL}
          align="left"
          offsetY={fontSize / 2}
        />
      )
    }
  }

  return <>{[...lines, ...labels]}</>
}
