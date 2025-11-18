import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import { Visualization } from './pages/Visualization'
import { RemoteControl } from './pages/RemoteControl'
import { colors } from './constants/colors'

function App() {
  return (
    <BrowserRouter>
      {/* Navigation bar */}
      <nav
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          padding: '12px 20px',
          background: colors.SURFACE,
          borderBottom: `2px solid ${colors.GRID}`,
          zIndex: 1001,
          display: 'flex',
          gap: '20px',
        }}
      >
        <Link
          to="/"
          style={{
            color: colors.TEXT_PRIMARY,
            textDecoration: 'none',
            fontSize: 16,
            fontWeight: 500,
          }}
        >
          Visualization
        </Link>
        <Link
          to="/remote"
          style={{
            color: colors.TEXT_PRIMARY,
            textDecoration: 'none',
            fontSize: 16,
            fontWeight: 500,
          }}
        >
          Remote Control
        </Link>
      </nav>

      {/* Main content */}
      <div style={{ paddingTop: '60px' }}>
        <Routes>
          <Route path="/" element={<Visualization />} />
          <Route path="/remote" element={<RemoteControl />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
