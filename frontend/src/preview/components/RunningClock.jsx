import { useEffect, useState } from "react"
import moment from "moment";
import { Typography } from "@mui/material";


const RunningClock = (props) => {

    const [value, setValue] = useState(moment(moment.unix(props.started)).fromNow())

    useEffect(() => {
        const intervalId = setInterval(() => {
            setValue(moment(moment.unix(props.started)).fromNow())
        }, 60000)
        return () => clearInterval(intervalId)
    }, [])

    return (
        <Typography variant='caption'>
            {`Running since ${value}`}
        </Typography>
    )


}

export default RunningClock