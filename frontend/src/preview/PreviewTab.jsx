import '../App.css'
import './PreviewTab.css'
import StillStatus from './StillStatus'
const PreviewTab = (props) => {
    const STREAM_URL = `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/preview/live.mjpeg`

    const frameDurationToFPS = (microseconds) => {
        return (1000000 / microseconds).toFixed(2)
    }

    const dummy = {
        "video": [{
            "id": "6dfeb5b0-ea70-11ee-b99b-e567683b501b",
            "resolution": "720p",
            "quality": 3,
            "started": 1711347910.0940897,
            "stopped": null,
            "size": 0,
            "running": true
        }],
        "still": {
            "limit": 0,
            "interval": 3600,
            "full_res": false,
            "name": "[count]",
            "count": 1,
            "running": true,
            "started": 1711347897.0842917,
            "previous": null,
            "stopped": null,
            "next": 1711351498.0852869
        },
        "preview": { "running": true },
        "running": true,
        "metadata": {
            "FocusFoM": 818,
            "ExposureTime": 32987,
            "ColourTemperature": 4988,
            "SensorTimestamp": 1154038080000,
            "ScalerCrop": [108, 440, 3840, 2160],
            "SensorBlackLevels": [4096, 4096, 4096, 4096],
            "DigitalGain": 1,
            "ColourGains": [3.0041348934173584, 1.503603219985962],
            "SensorTemperature": 0,
            "Lux": 26.391979217529297,
            "FrameDuration": 33321,
            "AeLocked": true,
            "ColourCorrectionMatrix": [1.9217796325683594, -0.7921517491340637, -0.1296256184577942, -0.30207228660583496, 1.8429197072982788, -0.5408419966697693, -0.06879816949367523, -0.5830798149108887, 1.651877999305725],
            "AnalogueGain": 8
        },
        "configration": {
            "use_case": "video",
            "buffer_count": 6,
            "queue": true,
            "main": {
                "format": "XBGR8888",
                "size": [1280, 720],
                "stride": 5120,
                "framesize": 3686400
            },
            "lores": {
                "format": "YUV420",
                "size": [426, 240],
                "stride": 448,
                "framesize": 161280
            },
            "raw": {
                "format": "SBGGR12_CSI2P",
                "size": [2028, 1080],
                "stride": 3072,
                "framesize": 3317760
            },
            "display": "main", "encode": "main"
        }
    }


    return (
        <>
            <div className='header' />
            <div className='video-container'>
                <div className='video'>
                    <img src={STREAM_URL} width="640" />
                </div>
                <div className='recording-text'>
                    <span>Recording</span>
                </div>
                <div className='preview-status'>
                    <span>FPS: {props.status?.metadata?.FrameDuration ? frameDurationToFPS(props.status.metadata.FrameDuration) : 'N/A'}</span>
                    <span>Watching: 0</span>
                </div>
            </div>
            <StillStatus status={props.status?.still ?? {}}/>
        </>)
}

export default PreviewTab