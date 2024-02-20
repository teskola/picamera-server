import { useState } from 'react'
import './App.css'
import ConfigureTab from './ConfigureTab'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <div className='container'>
      <div className='video'>
        <p>Hello</p>
      </div>
      <div className='menu'>
        <ConfigureTab/>
      </div>
    </div>
        
    </>
  )
}

export default App
