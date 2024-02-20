import { useRef } from "react"
import TextField from '@mui/material/TextField';
import "./StillPage.css"

const StillPage = (props) => {
    const pathRef = useRef();
    const intervalRef = useRef();

    return (
        <form className="form">
            <TextField className="inputfield" id="path" ref={pathRef} variant="outlined" value="/[HH:mm:ss]" label="Path" fullWidth />
            <TextField id="interval" ref={intervalRef} variant="outlined" label="Interval" fullWidth />
        </form>
    )
}

export default StillPage