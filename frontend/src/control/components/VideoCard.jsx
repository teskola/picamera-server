import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import { Button, Card, InputAdornment, TextField, Typography } from '@mui/material';
import './VideoCard.css'
import { useRef, useState } from 'react';
import moment from 'moment';
import DurationClock from './DurationClock';
import { durationString } from '../../utilities';
import { deleteVideo, uploadVideo } from '../../api';
import DeleteDialog from './DeleteDialog';

const VideoCard = (props) => {
    const pathRef = useRef()
    const [deleting, setDeleting] = useState(false)
    const [error, setError] = useState()
    const [loading, setLoading] = useState()

    // https://stackoverflow.com/questions/15900485/correct-way-to-convert-size-in-bytes-to-kb-mb-gb-in-javascript

    const formatBytes = (bytes, decimals = 2) => {
        if (!+bytes) return '0 Bytes'

        const k = 1024
        const dm = decimals < 0 ? 0 : decimals
        const sizes = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']

        const i = Math.floor(Math.log(bytes) / Math.log(k))

        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
    }    

    const onCancel = () => {
        setDeleting(false)
    }

    const onConfirm = () => {
        deleteVideo(props.video.id)
    }

    const onDeleteClicked = () => {
        setDeleting(true)
    }

    const onUpload = async () => {
        setLoading(true)
        const res = await uploadVideo(props.video.id, pathRef.current.value)
        setLoading(false)
        switch (res.status) {
            case 200:
                setError()
                break
            case 400:
                setError(res.body.error)
                break
            default:
                setError('Something went wrong!')
                break
        }

    }

    const dummy = [
        {
          "message": "\"name\" is not allowed to be empty",
          "path": [
            "name"
          ],
          "type": "string.empty",
          "context": {
            "label": "name",
            "value": "",
            "key": "name"
          }
        }
      ]

    return (
        <>
            <DeleteDialog open={deleting} onConfirm={onConfirm} onCancel={onCancel} />
            <Card style={{ backgroundColor: deleting ? "rgba(255, 0, 0, 0.5)" : "transparent" }}>
                <div className='video-card__container'>
                    <div className='video-card__icon'>
                        <VideocamOutlinedIcon fontSize='large' />
                        <Typography variant='caption'>{props.video.resolution}</Typography>
                        <Typography variant='caption'>{'('}{props.video.quality}{')'}</Typography>
                    </div>
                    <div>
                        <div className='video-card__input'>
                            <TextField
                                disabled={deleting || loading || !props.video.stopped}
                                error={error}
                                helperText={error && error[0].message}
                                inputRef={pathRef}
                                variant="standard"
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
                                <Typography variant='caption'>: {props.video.stopped ? moment.unix(props.video.stopped).format('DD/MM/YYYY HH:mm:ss') : 'N/A'}</Typography>
                                {props.video.stopped ?
                                    <Typography variant='caption'>: {durationString({ end: props.video.stopped, start: props.video.started })}
                                    </Typography> :
                                    <DurationClock prefix=': ' start={props.video.started} />
                                }
                                <Typography variant='caption'>: {formatBytes(props.video.size)}</Typography>
                            </div>


                        </div>
                    </div>
                    <div className='video-card__btns_status'>
                        <div className='video-card__card__btns_status--buttons'>
                            <Button style={{ minWidth: '102px', }} disabled={!props.video.stopped || deleting || loading} onClick={onUpload} startIcon={<CloudUploadIcon />}>Upload</Button>
                            <Button style={{ minWidth: '102px', }} disabled={!props.video.stopped || deleting || loading} onClick={onDeleteClicked} color='error' startIcon={<DeleteOutlinedIcon />}>Delete</Button>
                        </div>
                        <div className='video-card__btns_status--status'>
                            <Typography variant='caption'>Stopped.</Typography>
                        </div>
                    </div>

                </div>
            </Card>
        </>
    )

}

export default VideoCard