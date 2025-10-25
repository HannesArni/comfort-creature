import { useState, useEffect, useRef, ReactNode } from 'react'
import { Stage } from 'react-konva'
import Konva from 'konva'

const ZOOM_FACTOR = 1.05
const MIN_SCALE = 0.1
const MAX_SCALE = 10

interface ZoomableCanvasProps {
  children: (scale: number, position: { x: number; y: number }) => ReactNode
  onCanvasClick?: (worldX: number, worldY: number) => void
}

export function ZoomableCanvas({ children, onCanvasClick }: ZoomableCanvasProps) {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  })
  const [scale, setScale] = useState(1)
  // Center the origin (0,0) in the middle of the screen
  const [position, setPosition] = useState({
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  })
  const stageRef = useRef<Konva.Stage>(null)
  const isDragging = useRef(false)
  const lastPointerPosition = useRef({ x: 0, y: 0 })

  useEffect(() => {
    const handleResize = () => {
      const newWidth = window.innerWidth
      const newHeight = window.innerHeight

      // Maintain origin position relative to center when resizing
      setPosition((prev) => ({
        x: prev.x + (newWidth - dimensions.width) / 2,
        y: prev.y + (newHeight - dimensions.height) / 2,
      }))

      setDimensions({
        width: newWidth,
        height: newHeight,
      })
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [dimensions])

  const handleWheel = (e: Konva.KonvaEventObject<WheelEvent>) => {
    e.evt.preventDefault()

    const stage = stageRef.current
    if (!stage) return

    const oldScale = scale
    const pointer = stage.getPointerPosition()
    if (!pointer) return

    const mousePointTo = {
      x: (pointer.x - position.x) / oldScale,
      y: (pointer.y - position.y) / oldScale,
    }

    const direction = e.evt.deltaY > 0 ? 1 / ZOOM_FACTOR : ZOOM_FACTOR
    const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, oldScale * direction))

    setScale(newScale)
    setPosition({
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale,
    })
  }

  const handleMouseDown = (e: Konva.KonvaEventObject<MouseEvent>) => {
    const stage = stageRef.current
    if (!stage) return

    // Only start panning if clicking on the Stage itself (empty space)
    const clickedOnEmpty = e.target === stage
    if (clickedOnEmpty) {
      isDragging.current = true
      const pos = stage.getPointerPosition()
      if (pos) {
        lastPointerPosition.current = pos
      }
    }
  }

  const handleClick = (e: Konva.KonvaEventObject<MouseEvent>) => {
    const stage = stageRef.current
    if (!stage) return

    // Only handle clicks on empty space (the Stage itself)
    const clickedOnEmpty = e.target === stage
    if (clickedOnEmpty && onCanvasClick) {
      const pos = stage.getPointerPosition()
      if (pos) {
        // Convert screen coordinates to world coordinates (canvas Y-down system)
        const worldX = (pos.x - position.x) / scale
        const worldY = -(pos.y - position.y) / scale
        onCanvasClick(worldX, worldY)
      }
    }
  }

  const handleMouseMove = () => {
    if (!isDragging.current) return

    const stage = stageRef.current
    if (!stage) return

    const pos = stage.getPointerPosition()
    if (!pos) return

    const dx = pos.x - lastPointerPosition.current.x
    const dy = pos.y - lastPointerPosition.current.y

    setPosition((prev) => ({
      x: prev.x + dx,
      y: prev.y + dy,
    }))

    lastPointerPosition.current = pos
  }

  const handleMouseUp = () => {
    isDragging.current = false
  }

  return (
    <Stage
      ref={stageRef}
      width={dimensions.width}
      height={dimensions.height}
      scaleX={scale}
      scaleY={scale}
      x={position.x}
      y={position.y}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onClick={handleClick}
    >
      {children(scale, position)}
    </Stage>
  )
}
