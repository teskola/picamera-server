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
    const [videos, setVideos] = useState([])

    useEffect(() => {
        setRunning(props.running)
        if (props.running) {
            const runningVideo = props.videos.find((e) => e.running)
            setResolution(runningVideo.resolution)
            setQuality(runningVideo.quality)
        }

      }, [props]);  

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
                break
            case 409:
                setError(res.body.error.running_error)
                setRunning(true)
                break
            default:
                setError('Something went wrong!')
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
                break
            case 409:
                setError(res.body.error.running_error)
                setRunning(false)
                break
            default:
                setError('Something went wrong!')
                break
        }
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