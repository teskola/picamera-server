import VideoCard from "./VideoCard"
import './VideoList.css'

const dummy = [
    {
        "id": "d8269080-e68c-11ee-961b-f315d239b0d0",
        "resolution": "720p",
        "quality": 3,
        "started": 1710920309.775413,
        "stopped": 1710920313.8885648,
        "size": 692914,
        "running": false
    },
    {
        "id": "7997c520-e691-11ee-961b-f315d239b0d0",
        "resolution": "720p",
        "quality": 3,
        "started": 1710922298.3494303,
        "stopped": 1710922301.572803,
        "size": 1220018,
        "running": false
    },
    {
        "id": "7ea960a0-e691-11ee-961b-f315d239b0d0",
        "resolution": "1080p",
        "quality": 5,
        "started": 1710922306.8299432,
        "stopped": 1710922310.0257306,
        "size": 3328772,
        "running": false
    },
    {
        "id": "83bde250-e691-11ee-961b-f315d239b0d0",
        "resolution": "720p",
        "quality": 1,
        "started": 1710922315.3307102,
        "stopped": 1710922319.2310286,
        "size": 484467,
        "running": false
    },
    {
        "id": "b5385b80-e691-11ee-961b-f315d239b0d0",
        "resolution": "720p",
        "quality": 1,
        "started": 1710922398.363967,
        "stopped": 1710922403.5098126,
        "size": 732135,
        "running": false
    },
    {
        "id": "cc8e2c60-e691-11ee-961b-f315d239b0d0",
        "resolution": "720p",
        "quality": 1,
        "started": 1710922437.3277586,
        "stopped": 1710922452.692966,
        "size": 2376455,
        "running": false
    },
    {
        "id": "e2761560-e691-11ee-961b-f315d239b0d0",
        "resolution": "720p",
        "quality": 1,
        "started": 1710922474.2651415,
        "stopped": 1710922490.8846526,
        "size": 2578903,
        "running": false
    },
    {
        "id": "b4c2e7f0-e692-11ee-961b-f315d239b0d0",
        "resolution": "720p",
        "quality": 1,
        "started": 1710922827.0870142,
        "stopped": 1710922832.0572982,
        "size": 646618,
        "running": false
    }
]

const VideoList = (props) => {
    return (
        <div>            
            {dummy?.map((video) => (
                <div className="video__list-item">
                <VideoCard key={video.id} video={video} />
                </div>
            ))}
        </div>
    )
}

export default VideoList