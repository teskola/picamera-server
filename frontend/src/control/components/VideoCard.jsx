import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import { Button, Card, InputAdornment, TextField, Typography } from '@mui/material';
import './VideoCard.css'
import { useRef } from 'react';
import moment from 'moment';

const VideoCard = (props) => {
    const pathRef = useRef()

    // https://stackoverflow.com/questions/15900485/correct-way-to-convert-size-in-bytes-to-kb-mb-gb-in-javascript

    const formatBytes = (bytes, decimals = 2) => {
        if (!+bytes) return '0 Bytes'

        const k = 1024
        const dm = decimals < 0 ? 0 : decimals
        const sizes = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']

        const i = Math.floor(Math.log(bytes) / Math.log(k))

        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
    }

    const duration = () => {
        var milliseconds = 1000 * (props.video.stopped - props.video.started)
        var duration = moment.duration(milliseconds);
        return moment.utc(duration.asMilliseconds()).format('HH:mm:ss')
    }

    const quality = {
        1: "Very low",
        2: "Low",
        3: "Medium",
        4: "High",
        5: "Very High"
    }

    return (
        <Card>
            <div className='video-card__container'>
                <div className='video-card__icon'>
                    <VideocamOutlinedIcon fontSize='large' />
                    <Typography variant='caption'>{props.video.resolution}</Typography>
                    <Typography variant='caption'>{'('}{props.video.quality}{')'}</Typography>
                </div>
                <div>
                    <div className='video-card__input'>
                        <TextField inputRef={pathRef} variant="standard"
                            style={{ width: 200 }}
                            InputProps={{
                                startAdornment: (<InputAdornment position='end'>video/</InputAdornment>),
                                endAdornment: (<InputAdornment position='start'>.h264</InputAdornment>)

                            }} />
                    </div>
                    <div className='video-card__info'>
                        <div className='video-card__info--column'>
                            <Typography variant='caption'>Started</Typography>
                            <Typography variant='caption'>Stopped</Typography>
                            <Typography variant='caption'>Duration</Typography>
                            <Typography variant='caption'>Size</Typography>
                        </div>
                        <div className='video-card__info--column'>
                            <Typography variant='caption'>: {moment.unix(props.video.started).format('DD/MM/YYYY HH:mm:ss')}</Typography>
                            <Typography variant='caption'>: {moment.unix(props.video.stopped).format('DD/MM/YYYY HH:mm:ss')}</Typography>
                            <Typography variant='caption'>: {duration()}</Typography>
                            <Typography variant='caption'>: {formatBytes(props.video.size)}</Typography>
                        </div>


                    </div>
                </div>
                <div className='video-card__btns_and_status'>
                    <div className='video-card__buttons'>
                        <Button style={{ minWidth: '102px', }} startIcon={<CloudUploadIcon />}>Upload</Button>
                        <Button style={{ minWidth: '102px', }} color='error' startIcon={<DeleteOutlinedIcon />}>Delete</Button>
                    </div>
                    <div>
                        <Typography variant='caption'>Stopped.</Typography>
                    </div>
                </div>

            </div>
        </Card>
    )

}

export default VideoCard