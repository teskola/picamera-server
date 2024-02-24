import MainNavigation from "./MainNavigation"
import ProfilePage from "./ProfilePage"
import StillPage from "./StillPage"
import VideoPage from "./VideoPage"

import { Route, Switch, Redirect } from 'react-router-dom/cjs/react-router-dom'


const ConfigureTab = (props) => {
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

export default ConfigureTab