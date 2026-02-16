import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import Gallery from './components/Gallery/Gallery'
import ImageUploader from './components/ImageUploader/ImageUploader'
import './App.css'

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="app">
          <header className="app-header">
            <h1>MemoryBook</h1>
            <nav>
              <Link to="/">Gallery</Link>
              <Link to="/upload">Upload</Link>
            </nav>
          </header>
          <main className="app-main">
            <Routes>
              <Route path="/" element={<Gallery />} />
              <Route path="/upload" element={<ImageUploader />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  )
}

export default App
