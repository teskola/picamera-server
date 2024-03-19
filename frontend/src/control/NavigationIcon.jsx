import CameraAltOutlinedIcon from '@mui/icons-material/CameraAltOutlined';
import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import './NavigationIcon.css'

const NavigationIcon = (props) => {
    return (
        <div className='icon'>
            <div>
                {
                    {
                        'still': <CameraAltOutlinedIcon fontSize='large' />,
                        'video': <VideocamOutlinedIcon fontSize='large' />,
                        'profile': <PersonOutlinedIcon fontSize='large' />
                    }[props.icon]
                }
            </div>
            <div>
                {props.icon}
            </div>
        </div>
    )
}

export default NavigationIcon