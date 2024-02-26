import './App.css'
import ConfigureTab from './ConfigureTab'

function App() {

  return (
    <>
      <div className='container'>
        <div className='video'>
          <img src="http://192.168.1.129:8000/stream.mjpg" width="640"/>
        </div>
        <div className='menu'>          
          <ConfigureTab />
        </div>
      </div>

    </>
  )
}

export default App
