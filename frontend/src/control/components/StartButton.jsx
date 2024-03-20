import { Button } from "@mui/material"
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const StartButton = (props) => {
    return (
        <Button style={{ minWidth: '102px', }} variant="contained" startIcon={<PlayArrowIcon />} disabled={props.disabled} onClick={props.onClick}>
            Start
        </Button>
    )
}

export default StartButton