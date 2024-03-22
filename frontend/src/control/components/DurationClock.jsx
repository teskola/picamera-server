import { Typography } from "@mui/material";
import moment from "moment";
import { useEffect, useState } from "react";
import { durationString } from "../../utilities";

const DurationClock = (props) => {    
 
    const [current, setCurrent] = useState(moment().valueOf() / 1000)
    useEffect(() => {
        const intervalId = setInterval(() => {
            setCurrent(moment().valueOf() / 1000);
        }, 1000)
        return () => clearInterval(intervalId)
    }, [])

    return (
        <Typography variant='caption'>
            {props?.prefix}{durationString({end: current, start: props.start})}
        </Typography>
    )


}

export default DurationClock