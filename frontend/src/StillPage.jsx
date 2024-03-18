import { useRef, useState } from "react"
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import "./StillPage.css"
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment'
import { FormControl, FormHelperText, InputAdornment, InputLabel, OutlinedInput, Radio, Typography } from "@mui/material";
import { startStill, stopStill } from "./api";
import moment from "moment";

const StillPage = (props) => {

    const dummy = [
        {
            message: '"name" is not allowed to be empty',
            path: ['name'],
            type: 'string.empty',
            context: { label: 'name', value: '', key: 'name' }
        },
        {
            message: 'hello',
            path: ['name'],
            type: 'string.empty',
            context: { label: 'name', value: '', key: 'name' }
        }
    ]

    const pathRef = useRef('')
    const intervalRef = useRef(1)
    const [multiplier, setMultiplier] = useState(1)
    const [delayMode, setDelayMode] = useState('seconds')
    const [resolution, setResolution] = useState('half')
    const [error, setError] = useState(dummy)
    const limitRef = useRef(0)
    const delayRef = useRef(1)
    const dateTimeRef = useRef()

    const hasError = (field) =>
        error && error.filter((e) => e.path.includes(field)).length > 0


    const errorMessage = (field) => error && error.filter((e) => e.path.includes(field)).map((e) => e.message)[0]


    const onResolutionChange = (event) => {
        setResolution(event.target.value)
    }

    const onUnitChange = (event) => {
        setMultiplier(event.target.value)
    }

    const onDelayModeChange = (event) => {
        setDelayMode(event.target.value)
    }

    const onStart = async (_) => {
        setError()
        const res = await startStill({
            interval: Math.floor(parseFloat(intervalRef.current.value) * multiplier),
            path: pathRef.current.value,
            limit: parseInt(limitRef.current.value),
            full_res: resolution === 'full',
            epoch: delayMode === 'epoch' ? moment.unix(parseInt(dateTimeRef.current.value)) : undefined,
            delay: delayMode === 'seconds' ? parseInt(delayRef.current.value) : undefined
        }
        )
        res.error && setError(res.error)
        console.log(res)
    }

    const onStop = async (_) => {
        setError()
        const res = await stopStill()
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
                    <FormControl>
                        <InputLabel htmlFor='path'>Path</InputLabel>
                        <OutlinedInput className="input"
                            inputRef={pathRef}
                            label='Path'
                            defaultValue={pathRef.current}
                            startAdornment={<InputAdornment position="start">still/</InputAdornment>}
                            error={hasError('name')} />
                        <FormHelperText error={hasError('name')}>
                            {errorMessage('name')}
                        </FormHelperText>
                    </FormControl>
                    <TextField className="format" id="format" value='.jpg' variant="outlined" label="Format" disabled />
                </div>
                <Typography variant="caption">[year] = year<br />[month] = month<br />[day] = day<br />[HH] = hours<br />[mm] = minutes<br />[ss] = seconds<br />[count] = image count</Typography>
                <div className="column_item">
                    <TextField className="input"
                        id="interval"
                        inputRef={intervalRef}
                        defaultValue={intervalRef.current}
                        variant="outlined"
                        label="Interval"
                        error={hasError('interval')}
                        helperText={errorMessage('interval')} />

                    <TextField className="format" value={multiplier} onChange={onUnitChange} select>
                        <MenuItem value={1} >seconds</MenuItem>
                        <MenuItem value={60}>minutes</MenuItem>
                        <MenuItem value={3600}>hours</MenuItem>
                    </TextField>
                </div>
                <TextField className="column_item" id="limit" inputRef={limitRef} defaultValue={limitRef.current} variant="outlined" label="Number of images" fullWidth />
                <Typography variant="caption">0 = unlimited</Typography>
                <div className="column_item">
                    <Radio checked={delayMode === 'seconds'} onChange={onDelayModeChange} value="seconds" />
                    <TextField disabled={delayMode !== 'seconds'}
                        id="delay" inputRef={delayRef}
                        defaultValue={delayRef.current}
                        variant="outlined"
                        label="First image delay in seconds"

                    />
                </div>
                <div className="column_item">
                    <Radio checked={delayMode === 'epoch'} onChange={onDelayModeChange} value="epoch" />
                    <LocalizationProvider adapterLocale="fi" dateAdapter={AdapterMoment}>
                        <DateTimePicker slotProps={{
                            textField: {
                                fullWidth: true,
                                helperText: errorMessage('epoch'),
                            },
                        }} disablePast defaultValue={Date(Date.now).toString()} inputRef={dateTimeRef} format='DD/MM/YYYY HH:mm' ampm={false} disabled={delayMode !== 'epoch'} label="First image at" />
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