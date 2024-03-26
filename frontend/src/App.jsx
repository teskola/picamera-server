import { useEffect, useState } from 'react'
import './App.css'
import ControlTab from './control/ControlTab'
import LogTab from './logs/LogTab'
import PreviewTab from './preview/PreviewTab'
import { getStatus } from './api'
import { socket } from './socket'



function App() {

  const [status, setStatus] = useState()

  const statusListener = (data) => {
    console.log(data)
    setStatus(data)
  }

  useEffect(() => {
    const fetch = async () => {
      const s = await getStatus()
      setStatus(s)
    }
    fetch()
    socket.on('status', statusListener)

    return () => {
      socket.off('status', statusListener)
    }


  }, []);


  return (
    <>
      <div className='preview'>
        <PreviewTab status={status} />
      </div>
      <div className='control'>
        <ControlTab status={status} />
      </div>
      <div className='log'>
        <LogTab />
      </div>

    </>
  )
}

export default App
