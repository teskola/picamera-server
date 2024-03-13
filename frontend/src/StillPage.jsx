import { useRef, useState } from "react"
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import "./StillPage.css"
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment'
import { Radio, Typography } from "@mui/material";

const StillPage = (props) => {

    const [path, setPath] = useState('/still/')
    const [interval, setInterval] = useState(1)
    const [multiplier, setMultiplier] = useState(1)
    const [delayMode, setDelayMode] = useState('seconds')
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

    const onIntervalChange = (event) => {
        setInterval(event.target.value)
    }

    const onUnitChange = (event) => {
        setInterval(intervalInSeconds / event.target.value)
        setMultiplier(event.target.value)
    }

    const onDelayModeChange = (event) => {
        setDelayMode(event.target.value)
    }

    const onDateTimeChange = (date, oldDate) => {
        console.log(date)
    }



    return (
        <div className="page">
            <form className="form">
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

            </form>
            <div className="buttons">
                <button>Start</button>
                <button>Stop</button>
            </div>
        </div>
    )
}

export default StillPage