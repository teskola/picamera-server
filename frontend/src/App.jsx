import './App.css'
import ConfigureTab from './ConfigureTab'

function App() {

const STREAM_URL = `http://${import.meta.env.VITE_RASPBERRY_URL}:5000/stream.mjpg`

  return (
    <>
      <div className='container'>
        <div className='video'>
          <img src={STREAM_URL} width="640"/>
        </div>
        <div className='menu'>          
          <ConfigureTab />
        </div>
      </div>

    </>
  )
}

export default App
