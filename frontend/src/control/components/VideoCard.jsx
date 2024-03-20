import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import { Card } from '@mui/material';

const VideoCard = (props) => {
    console.log(props)
    return (
        <Card>            
            <VideocamOutlinedIcon />
            {props.video.id}
        </Card>
    )

}

export default VideoCard