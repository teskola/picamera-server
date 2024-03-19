import '../App.css'
import './PreviewTab.css'
const PreviewTab = () => {
    const STREAM_URL = `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/preview/live.mjpeg`

    return (
        <>
            <div className='header' />
            <div className='video'>
                <img src={STREAM_URL} width="640" />
            </div>
        </>)
}

export default PreviewTab