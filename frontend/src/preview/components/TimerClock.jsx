import { useEffect, useState } from "react"
import moment from "moment";
import { Typography } from "@mui/material";


const TimerClock = (props) => {

    const diffString = () => {
        const m = moment.unix(props.target)
        const diff = m.diff(current) 
        return moment.utc(diff > 0 ? diff : 0).format('HH:mm:ss')
    }

    const [current, setCurrent] = useState(moment())
    useEffect(() => {
        const intervalId = setInterval(() => {
            setCurrent(moment());
        }, 1000)
        return () => clearInterval(intervalId)
    }, [])

    return (
        <Typography variant='caption'>
            {diffString()}
        </Typography>
    )


}

export default TimerClock