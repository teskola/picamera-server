import { useEffect, useState } from "react"
import "../ControlTab.css"
import { FormHelperText, MenuItem, TextField } from "@mui/material"
import { startVideo, stopVideo } from "../../api";
import StartButton from "../components/StartButton";
import StopButton from "../components/StopButton";
import VideoList from "../components/VideoList"

const VideoPage = (props) => {

    const [resolution, setResolution] = useState('720p')
    const [quality, setQuality] = useState(3)
    const [running, setRunning] = useState(false)
    const [error, setError] = useState()
    const [loading, setLoading] = useState(false)
    const [videos, setVideos] = useState(props.videos)

    useEffect(() => {        
        console.log(props.videos)
        updateState(props.videos)        
      }, []);

    const updateState = (v) => {
        let runningVideo
        if (v.length > 0) {
            runningVideo = v.find((e) => e.running)
        }
        
        if (runningVideo) {
            setRunning(true)
            setResolution(runningVideo.resolution)
            setQuality(runningVideo.quality)
            
        }
        else {
            setRunning(false)
        }
        setVideos(v)
    }

    const onResolutionChange = (event) => {
        setResolution(event.target.value)
    }

    const onQualityChange = (event) => {
        setQuality(event.target.value)
    }

    const onStart = async (_) => {
        setLoading(true)
        const res = await startVideo({ resolution: resolution, quality: quality })
        setLoading(false)
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

    }

    const onStop = async (_) => {
        setLoading(true)
        const res = await stopVideo()
        setLoading(false)
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
        <>
            <div>
                <div className="control__column_item">
                    <TextField
                        disabled={running || loading}
                        label="Resolution"
                        onChange={onResolutionChange}
                        value={resolution}
                        select
                        fullWidth>
                        <MenuItem value='720p' > HD  :  1280x720  (720p30)</MenuItem>
                        <MenuItem value='1080p'>FHD  : 1920x1080 (1080p30)</MenuItem>
                    </TextField>
                </div>
                <div className="control__column_item">
                    <TextField
                        disabled={running || loading}
                        label="Quality"
                        onChange={onQualityChange}
                        value={quality}
                        select
                        fullWidth>
                        <MenuItem value={1}>Very low (1)</MenuItem>
                        <MenuItem value={2}>Low (2)</MenuItem>
                        <MenuItem value={3}>Medium (3)</MenuItem>
                        <MenuItem value={4}>High (4)</MenuItem>
                        <MenuItem value={5}>Very high (5)</MenuItem>
                    </TextField>
                </div>
            </div>
            <div className="control__buttons">
                <StartButton disabled={running || loading} onClick={onStart} />
                <StopButton disabled={!running || loading} onClick={onStop} />
            </div>
            <div className="control__error">
                <FormHelperText error={error != undefined}>{loading ? 'Loading...' : error}</FormHelperText>
            </div>
            <VideoList videos={props.videos} />

        </>
    )
}

export default VideoPage