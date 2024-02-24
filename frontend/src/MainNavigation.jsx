import NavigationIcon from './NavigationIcon';
import './MainNavigation.css'
import { Link } from 'react-router-dom/cjs/react-router-dom';

const MainNavigation = (props) => {
    return (
        <div className='navigationbar'>
            <Link to="/still"><NavigationIcon icon='still' /></Link>
            <Link to="/video"><NavigationIcon icon='video' /></Link>
            <Link to="/profile"><NavigationIcon icon='profile' /></Link>
        </div>
    )
}

export default MainNavigation