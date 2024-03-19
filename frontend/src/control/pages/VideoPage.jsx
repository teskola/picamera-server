import { useState } from "react"
import "../ControlTab.css"
import { FormHelperText, MenuItem, TextField } from "@mui/material"
import { startVideo, stopVideo } from "../../api";


const VideoPage = (props) => {

    const [resolution, setResolution] = useState('720p')
    const [quality, setQuality] = useState(3)
    const [running, setRunning] = useState(false)
    const [error, setError] = useState()       

    const updateState = (videos) => {           
        const runningVideo = videos.find((e) => e.running)    
        if (runningVideo) {
            setRunning(true)
            setResolution(runningVideo.resolution)
            setQuality(runningVideo.quality)            
        }
        else {
            setRunning(false)            
        }
    }

    const onResolutionChange = (event) => {
        setResolution(event.target.value)
    }

    const onQualityChange = (event) => {
        setQuality(event.target.value)
    }

    const onStart = async (_) => {
        setRunning(true)
        const res = await startVideo({ resolution: resolution, quality: quality })
        switch (res.status) {
            case 200:
                setError()
                updateState(res.body.status.video)
                break
            case 409:
                setError(res.body.error.running_error)
                updateState(res.body.status.video)
                break
            default:
                setError('Something went wrong!')
                setRunning(false)
                break
        }
        console.log(res)
    }

    const onStop = async (_) => {
        setRunning(false)
        const res = await stopVideo()
        switch (res.status) {
            case 200:
                setError()
                updateState(res.body.status.video)
                break
            case 409:
                setError(res.body.error.running_error)
                updateState(res.body.status.video)
                break
            default:
                setError('Something went wrong!')
                setRunning(false)
                break
        }
        console.log(res)
    }


    return (
        <div className="page">
            <div className="form">
                <div className="column_item">
                    <TextField
                        disabled={running}
                        label="Resolution"
                        onChange={onResolutionChange}
                        value={resolution}
                        select
                        fullWidth>
                        <MenuItem value='720p' > HD  :  1280x720  (720p30)</MenuItem>
                        <MenuItem value='1080p'>FHD  : 1920x1080 (1080p30)</MenuItem>
                    </TextField>
                </div>
                <div className="column_item">
                    <TextField
                        disabled={running}
                        label="Quality"
                        onChange={onQualityChange}
                        value={quality}
                        select
                        fullWidth>
                        <MenuItem value={1}>Very low</MenuItem>
                        <MenuItem value={2}>Low</MenuItem>
                        <MenuItem value={3}>Medium</MenuItem>
                        <MenuItem value={4}>High</MenuItem>
                        <MenuItem value={5}>Very high</MenuItem>
                    </TextField>
                </div>
            </div>
            <div className="buttons">
                <button disabled={running} onClick={onStart}>Start</button>
                <FormHelperText error>{error}</FormHelperText>
                <button disabled={!running} onClick={onStop}>Stop</button>
            </div>

        </div>
    )
}

export default VideoPage