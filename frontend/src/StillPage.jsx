import { useRef, useState } from "react"
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import "./StillPage.css"
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment'
import { Radio, Typography } from "@mui/material";
import { startStill, stopStill } from "./api";
import unix from "moment";

const StillPage = (props) => {

    const [path, setPath] = useState('/still/')
    const [interval, setInterval] = useState(1)
    const [multiplier, setMultiplier] = useState(1)
    const [delayMode, setDelayMode] = useState('seconds')
    const [resolution, setResolution] = useState('half')
    const limitRef = useRef(0)
    const delayRef = useRef(1)
    const dateTimeRef = useRef()
    const intervalInSeconds = Math.floor(interval * multiplier)

    const onPathChange = (event) => {
        if (event.target.value.substring(0, 7) !== '/still/') {
            setPath('/still/' + event.target.value.substring(6))
        }
        else {
            setPath(event.target.value)
        }
    }

    const onResolutionChange = (event) => {
        setResolution(event.target.value)
    }

    const onIntervalChange = (event) => {
        setInterval(event.target.value)
    }

    const onUnitChange = (event) =>  {
        setInterval(intervalInSeconds / event.target.value)
        setMultiplier(event.target.value)
    }

    const onDelayModeChange = (event) => {
        setDelayMode(event.target.value)
    }

    const onStart = async (_) => {
        res = await startStill({
            interval: intervalInSeconds,
            path: path,
            limit: 0,
            full_res: resolution === 'full',
            epoch: delayMode === 'epoch' ? dateTimeRef.current.value.unix() : null,
            delay: delayMode === 'seconds' ? 1 : null
        }
        )
        console.log(res)
    }

    const onStop = async (_) => {
        res = await stopStill()
        console.log(res)
    }

    return (
        <div className="page">
            <div className="form">
                <div className="column_item">
                    <TextField label="Resolution" value={resolution} onChange={onResolutionChange} select fullWidth>
                        <MenuItem value='half'>Half resolution : 2028x1520</MenuItem>
                        <MenuItem value='full'>Full resolution : 4056x3040</MenuItem>
                    </TextField>
                </div>
                <div className="path">
                    <TextField className="input" id="path" onChange={onPathChange} value={path} variant="outlined" label="Path" />
                    <TextField className="format" id="format" value='.jpg' variant="outlined" label="Format" disabled />
                </div>
                <Typography variant="caption">[year] = year<br />[month] = month<br />[day] = day<br />[HH] = hours<br />[mm] = minutes<br />[ss] = seconds<br />[count] = image count</Typography>
                <div className="column_item">
                    <TextField className="input" id="interval" onChange={onIntervalChange} value={interval} variant="outlined" label="Interval" />
                    <Select className="format" value={multiplier} onChange={onUnitChange}>
                        <MenuItem value={1} >seconds</MenuItem>
                        <MenuItem value={60}>minutes</MenuItem>
                        <MenuItem value={3600}>hours</MenuItem>
                    </Select>
                </div>
                <TextField className="column_item" id="limit" ref={limitRef} defaultValue={limitRef.current} variant="outlined" label="Number of images" fullWidth />
                <Typography variant="caption">0 = unlimited</Typography>
                <div className="column_item">
                    <Radio checked={delayMode === 'seconds'} onChange={onDelayModeChange} value="seconds" />
                    <TextField disabled={delayMode !== 'seconds'}
                        id="delay" ref={delayRef}
                        defaultValue={delayRef.current}
                        variant="outlined"
                        label="First image delay in seconds"
                    />
                </div>
                <div className="column_item">
                    <Radio checked={delayMode === 'epoch'} onChange={onDelayModeChange} value="epoch" />
                    <LocalizationProvider adapterLocale="fi" dateAdapter={AdapterMoment}>
                        <DateTimePicker ref={dateTimeRef} format='DD/MM/YYYY HH:mm' ampm={false} disabled={delayMode !== 'epoch'} label="First image at" />
                    </LocalizationProvider>
                </div>

            </div>
            <div className="buttons">
                <button onClick={onStart}>Start</button>
                <button onClick={onStop}>Stop</button>
            </div>
        </div>
    )
}

export default StillPage