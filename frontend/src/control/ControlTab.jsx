import MainNavigation from "./MainNavigation"
import ProfilePage from "./pages/ProfilePage"
import StillPage from "./pages/StillPage"
import VideoPage from "./pages/VideoPage"

import { Route, Switch, Redirect } from 'react-router-dom'


const ControlTab = (props) => {
    return (<>
        <MainNavigation />
        <Switch>
            <Redirect exact from="/" to="still" />
            <Route path="/still" exact>
                <StillPage />
            </Route>
            <Route path="/video" exact>
                <VideoPage />
            </Route>
            <Route path="/profile" exact>
                <ProfilePage />
            </Route>
        </Switch>
    </>)
}

export default ControlTab