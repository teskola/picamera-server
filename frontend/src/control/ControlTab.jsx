import ProfilePage from "./pages/ProfilePage"
import StillPage from "./pages/StillPage"
import VideoPage from "./pages/VideoPage"
import '../App.css'

import ControlNavigation from "./components/ControlNavigation"
import { Routes, Route } from "react-router-dom";

const ControlTab = (props) => {
    return (<>
        <div className="header">
            <ControlNavigation />
        </div>
        <div className="control__content">
            <Routes>
                <Route path="/" element={<StillPage status={props.status.still}/>} />
                <Route path="/still" element={<StillPage status={props.status.still}/>} />
                <Route path="/video" element={<VideoPage videos={props.status.video}/>} />
                <Route path="/profile" element={<ProfilePage />} />
            </Routes>
        </div>


    </>)
}

export default ControlTab