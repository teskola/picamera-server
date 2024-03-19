import CameraAltOutlinedIcon from '@mui/icons-material/CameraAltOutlined';
import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import './NavigationIcon.css'

const NavigationIcon = (props) => {
    return (
        <>

            {
                {
                    'still':
                        <div class="item">
                            <CameraAltOutlinedIcon className='icon' fontSize='large' />
                            <span class="caption">{props.icon}</span>
                        </div>
                    ,
                    'video':
                        <div class="item">
                            <VideocamOutlinedIcon className='icon' fontSize='large' />
                            <span class="caption">{props.icon}</span>
                        </div>,
                    'profile':
                        <div class="item">
                            <PersonOutlinedIcon className='icon' fontSize='large' />
                            <span class="caption">{props.icon}</span>
                        </div>

                }[props.icon]
            }

        </>
    )
}

export default NavigationIcon