import NavigationIcon from './NavigationIcon';
import './MainNavigation.css'

const MainNavigation = (props) => {
    return (
        <div className='navigationbar'>
            <NavigationIcon icon='still' />
            <NavigationIcon icon='video' />
            <NavigationIcon icon='profile' />
        </div>
    )
}

export default MainNavigation