import './App.css'
import ControlTab from './control/ControlTab'

function App() {

  const STREAM_URL = `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/preview/live.mjpeg`

  return (
    <>
      <div className='container'>
        <div className='video'>
          <img src={STREAM_URL} width="640" />
        </div>
        <div className='menu'>
          <ControlTab />
        </div>
      </div>

    </>
  )
}

export default App
