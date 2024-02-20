import './App.css'
import ConfigureTab from './ConfigureTab'

function App() {

  return (
    <>
      <div className='container'>
        <div className='video'>
          <img src="stream.mjpg" width="640" height="480" />
        </div>
        <div className='menu'>
          <ConfigureTab />
        </div>
      </div>

    </>
  )
}

export default App
