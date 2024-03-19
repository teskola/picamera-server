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

    const pathRef = useRef('')
    const intervalRef = useRef(1)
    const [unit, setUnit] = useState('seconds')
    const [delayMode, setDelayMode] = useState('seconds')
    const [resolution, setResolution] = useState('half')
    const [error, setError] = useState()
    const [runningError, setRunningError] = useState()
    const limitRef = useRef(0)
    const delayRef = useRef(1)
    const [epoch, setEpoch] = useState(moment())
    const [running, setRunning] = useState(false)

    const unitToMultiplier = (value) => {
        switch (value) {
            case 'seconds':
                return 1
            case 'minutes':
                return 60
            case 'hours':
                return 3600
            default:
                new Error('Invalid unit')
        }
    }

    const hasError = (field) =>
        error && error.filter((e) => e.context.key === field).length > 0

    const getError = (field) => error && error.filter((e) => e.context.key === field)[0]

    const intervalErrorMessage = () => {
        if (!hasError('interval')) return
        const intervalError = error.filter((e) => e.context.key === 'interval')[0]
        switch (intervalError.type) {
            case 'number.max':
                return 'Interval must be less than ' + intervalError.context.limit / unitToMultiplier(unit) + ' ' + unit + '.'
            case 'number.min':
                return 'Interval must be greater than ' + (intervalError.context.limit / unitToMultiplier(unit)).toString().substring(0, 7) + ' ' + unit + '.'
            default:
                return intervalError.message
        }
    }


    const onResolutionChange = (event) => {
        setResolution(event.target.value)
    }

    const onUnitChange = (event) => {
        setUnit(event.target.value)
    }

    const onDelayModeChange = (event) => {
        setDelayMode(event.target.value)
    }

    const onStart = async (_) => {
        setRunning(true)
        const res = await startStill({
            interval: Math.floor(parseFloat(intervalRef.current.value) * unitToMultiplier(unit)),
            path: pathRef.current.value,
            limit: parseFloat(limitRef.current.value),
            full_res: resolution === 'full',
            epoch: delayMode === 'epoch' ? epoch.unix() : undefined,
            delay: delayMode === 'seconds' ? parseFloat(delayRef.current.value) : undefined
        }
        )
        switch (res.status) {
            case 200:                
                setError()
                setRunningError()
                setRunning(res.body.status.still.running)

                break
            case 400:
                setError(res.body.error)
                setRunning(false)
                setRunningError()
                break
            case 409:
                setError()
                setRunningError(res.body.error.running_error)
                setRunning(res.body.status.still.running)
                break
            default:
                setError()
                setRunning(false)
                setRunningError('Something went wrong!')
        }
        console.log(res)

    }

    const onStop = async (_) => {
        setRunning(false)
        const res = await stopStill()
        switch (res.status) {
            case 200:                
                setRunningError()
                setRunning(res.body.status.still.running)
                break
            case 409:
                setRunningError(res.body.error.running_error)
                setRunning(res.body.status.still.running)
                break
            default:
                setRunningError('Something went wrong!')
                setRunning(true)
                break
        }
        console.log(res)
    }

    return (
        <div className="page">
            <div className="form">
                <div className="column_item">
                    <TextField disabled={running} label="Resolution" value={resolution} onChange={onResolutionChange} select fullWidth>
                        <MenuItem value='half'>Half resolution : 2028x1520</MenuItem>
                        <MenuItem value='full'>Full resolution : 4056x3040</MenuItem>
                    </TextField>
                </div>
                <div className="path">
                    <FormControl>
                        <InputLabel htmlFor='path'>Path</InputLabel>
                        <OutlinedInput className="input"
                            disabled={running}
                            inputRef={pathRef}
                            inputProps={{ maxLength: 70 }}                            
                            label='Path'
                            defaultValue={pathRef.current}
                            startAdornment={<InputAdornment position="start">still/</InputAdornment>}
                            error={hasError('name')} />
                        <FormHelperText error={hasError('name')}>
                            {getError('name')?.message}
                        </FormHelperText>
                    </FormControl>
                    <TextField className="format" id="format" value='.jpg' variant="outlined" label="Format" disabled />
                </div>
                <Typography variant="caption">[YYYY] = year<br />[MM] = month<br />[DD] = day<br />[HH] = hours<br />[mm] = minutes<br />[ss] = seconds<br />[count] = image count</Typography>
                <div className="column_item">
                    <TextField className="input"
                        disabled={running}
                        id="interval"
                        inputRef={intervalRef}
                        defaultValue={intervalRef.current}
                        variant="outlined"
                        label="Interval"
                        error={hasError('interval')}
                        helperText={intervalErrorMessage()} />

                    <TextField className="format" disabled={running} value={unit} onChange={onUnitChange} select>
                        <MenuItem value={'seconds'} >seconds</MenuItem>
                        <MenuItem value={'minutes'}>minutes</MenuItem>
                        <MenuItem value={'hours'}>hours</MenuItem>
                    </TextField>
                </div>
                <TextField className="column_item"
                    disabled={running}
                    inputRef={limitRef}
                    defaultValue={limitRef.current}
                    variant="outlined"
                    label="Number of images"
                    error={hasError('limit')}
                    helperText={getError('limit')?.message}
                    fullWidth />
                <Typography variant="caption">0 = unlimited</Typography>
                <div className="column_item">
                    <Radio disabled={running} checked={delayMode === 'seconds'} onChange={onDelayModeChange} value="seconds" />
                    <TextField
                        error={hasError('delay') && delayMode === 'seconds'}
                        helperText={getError('delay')?.message}
                        fullWidth
                        disabled={running || delayMode !== 'seconds'}
                        id="delay" inputRef={delayRef}
                        defaultValue={delayRef.current}
                        variant="outlined"
                        label="First image delay in seconds"

                    />
                </div>
                <div className="column_item">
                    <Radio disabled={running} checked={delayMode === 'epoch'} onChange={onDelayModeChange} value="epoch" />
                    <LocalizationProvider adapterLocale="fi" dateAdapter={AdapterMoment}>
                        <DateTimePicker slotProps={{
                            textField: {
                                error: hasError('epoch') == true && delayMode === 'epoch',
                                fullWidth: true,
                                helperText: getError('epoch')?.type === 'number.min' ? 'Selected time is in the past.' : '',
                            },
                        }}
                            defaultValue={epoch}
                            onChange={(value) => setEpoch(value)}
                            disablePast
                            maxDateTime={moment.unix(2147483648)}
                            format='DD/MM/YYYY HH:mm'
                            ampm={false}
                            disabled={running || delayMode !== 'epoch'}
                            label="First image at" />
                    </LocalizationProvider>
                </div>

            </div>
            <div className="buttons">
                <button disabled={running} onClick={onStart}>Start</button>
                <FormHelperText error>{runningError}</FormHelperText>
                <button disabled={!running} onClick={onStop}>Stop</button>
            </div>
        </div>
    )
}

export default StillPage