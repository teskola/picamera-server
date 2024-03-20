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
        <div>
            <Routes>
                <Route path="/" element={<StillPage/>} />
                <Route path="/still" element={<StillPage/>} />
                <Route path="/video" element={<VideoPage />} />
                <Route path="/profile" element={<ProfilePage />} />
            </Routes>
        </div>


    </>)
}

export default ControlTab