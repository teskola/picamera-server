import './App.css'
import ControlTab from './control/ControlTab'
import LogTab from './logs/LogTab'
import PreviewTab from './preview/PreviewTab'

function App() {


  return (
    <>
      <div className='preview'>
        <PreviewTab />
      </div>
      <div className='control'>
        <ControlTab />
      </div>
      <div className='log'>
        <LogTab />
      </div>

    </>
  )
}

export default App
