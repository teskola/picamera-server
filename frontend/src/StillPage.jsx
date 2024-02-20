import { useRef, useState } from "react"
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import "./StillPage.css"

const StillPage = (props) => {
    const pathRef = useRef();
    const intervalRef = useRef();
    const [unit, setUnit] = useState('m');

    const handleChange = (event) => {
        setUnit(event.target.value);
    };

    return (
        <form className="form">
            <TextField margin="normal" id="path" ref={pathRef} variant="outlined" value="/[HH:mm:ss].jpg" label="Path" fullWidth />
            <div className="select">
                <TextField className="input" id="interval" ref={intervalRef} variant="outlined" label="Interval" fullWidth />
                <Select className="selector" value={unit} onChange={handleChange} fullWidth>
                    <MenuItem value="ms">milliseconds</MenuItem>
                    <MenuItem value="s">seconds</MenuItem>
                    <MenuItem value="m">minutes</MenuItem>
                    <MenuItem value="h">hours</MenuItem>
                </Select>
            </div>
        </form>        
    )
}

export default StillPage