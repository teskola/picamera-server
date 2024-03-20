import { Button } from "@mui/material"
import StopIcon from '@mui/icons-material/Stop';

const StopButton = (props) => {
    return (
        <Button color="error" style={{ minWidth: '102px', }} variant="contained" startIcon={<StopIcon />} disabled={props.disabled} onClick={props.onClick}>
            Stop
        </Button>
    )
}

export default StopButton