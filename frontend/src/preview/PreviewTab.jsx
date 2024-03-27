import '../App.css'
import './PreviewTab.css'
import StillStatus from './StillStatus'
const PreviewTab = (props) => {
    const STREAM_URL = `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/preview/live.mjpeg`

    return (
        <>
            <div className='header' />
            <div className='video-container'>
                <div className='video'>
                    <img src={STREAM_URL} width="640" />
                </div>
                {props.status?.recording && <div className='recording-text'><span>Recording</span></div>}
            </div>
            <StillStatus status={props.status?.still ?? {}} />
        </>)
}

export default PreviewTab