import { useState } from 'react'
import { Layer, Rect } from 'react-konva'
import './App.css'
import { ZoomableCanvas } from './components/ZoomableCanvas'
import { Grid } from './components/Grid'

function App() {
  const [rectPosition, setRectPosition] = useState({ x: 0, y: 0 })

  return (
    <ZoomableCanvas>
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
        </>
      )}

      <Layer>
        <Rect
          x={rectPosition.x}
          y={rectPosition.y}
          width={80}
          height={80}
          fill="black"
          draggable
        />
      </Layer>
    </ZoomableCanvas>
  )
}

export default App
