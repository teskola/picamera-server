import { useEffect, useState } from 'react'
import './App.css'
import ControlTab from './control/ControlTab'
import LogTab from './logs/LogTab'
import PreviewTab from './preview/PreviewTab'
import { getStatus } from './api'



function App() {

  useEffect(() => {
    const fetch = async () => {
      const s = await getStatus()
      console.log(s)
      setStatus(s)
    }
    fetch()

  }, []);

  useEffect(() => {
    const intervalId = setInterval(async () => {
      const s = await getStatus()
      console.log(s)
      setStatus(s)
    }, 10000)
    return () => clearInterval(intervalId)
  }, [])

  const [status, setStatus] = useState()


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
