import { IconButton } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import CameraAltOutlinedIcon from '@mui/icons-material/CameraAltOutlined';
import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';

const ControlNavigation = () => {   
    const { pathname } = useLocation()
    const navigate = useNavigate()
    return (
        <>
            <IconButton color={pathname === '/still' || pathname === '/' ? 'primary' : 'default'} onClick={() => navigate('/still')} aria-label='still' size='large' >
                <CameraAltOutlinedIcon fontSize='large' />
            </IconButton>
            <IconButton color={pathname === '/video' ? 'primary' : 'default'} onClick={() => navigate('/video')} aria-label='video' size='large' >
                <VideocamOutlinedIcon fontSize='large' />
            </IconButton>
            <IconButton color={pathname === '/profile' ? 'primary' : 'default'} onClick={() => navigate('/profile')} aria-label='profile' size='large' >
                <PersonOutlinedIcon fontSize='large' />
            </IconButton>
        </>
    )
}

export default ControlNavigation