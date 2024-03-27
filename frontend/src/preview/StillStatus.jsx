import { Typography } from '@mui/material'
import ScheduleIcon from '@mui/icons-material/Schedule';
import moment from 'moment';
import './StillStatus.css'
import TimerClock from './components/TimerClock';
import RunningClock from './components/RunningClock';
const StillStatus = (props) => {   

    const resolution = () => {
        if (props.status.full_res == undefined) return 'N/A'
        if (props.status.full_res) return '4056x3040'
        return '2028x1520'
    }

    const count = () => {
        if (props.status.count == undefined) return 'N/A'
        if (props.status.limit == 0) return props.status.count
        return `${props.status.count} / ${props.status.limit}`
    }   

    return (
        <div className='status__container'>
            <div className='status__content'>
                <div className='status__title'>
                    <ScheduleIcon /><span>Still scheduler</span>
                </div>
                <div className="status__table">
                    <div className="status__column-key">
                        <Typography variant='caption'>Status</Typography>
                        <Typography variant='caption'>Resolution</Typography>
                        <Typography variant='caption'>Count</Typography>
                        <Typography variant='caption'>Path</Typography>
                        <Typography variant='caption'>Last capture</Typography>
                        <Typography variant='caption'>Next capture</Typography>
                    </div>
                    <div className="status__column-value">
                        {props.status.running ? <RunningClock started={props.status.started}/> : <Typography variant='caption'>Stopped.</Typography>}
                        <Typography variant='caption'>{resolution()}</Typography>
                        <Typography variant='caption'>{count()}</Typography>
                        <Typography variant='caption'>{props.status.name ? `still/${props.status.name}.jpg` : 'N/A'}</Typography>
                        <Typography variant='caption'>{props.status.previous ? moment.unix(props.status.previous).format('DD/MM/YYYY HH:mm:ss') : 'N/A'}</Typography>
                        {props.status.next ? <TimerClock target={props.status.next}/> : <Typography variant='caption'>N/A</Typography>}
                    </div>
                </div>
            </div>
        </div>)
}
export default StillStatus