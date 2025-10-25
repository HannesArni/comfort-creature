import { Layer, Image } from 'react-konva'
import './App.css'
import { ZoomableCanvas } from './components/ZoomableCanvas'
import { Grid } from './components/Grid'
import useImage from 'use-image'

function App() {
  const [image] = useImage('/public/chat-gpt-chair.png')

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

          <Layer>
            <Image
              image={image}
              x={0}
              y={0}
              width={80}
              height={100}
              offsetX={40}
              offsetY={50}
              draggable
            />
          </Layer>
        </>
      )}
    </ZoomableCanvas>
  )
}

export default App
