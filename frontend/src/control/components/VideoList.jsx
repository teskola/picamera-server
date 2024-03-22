import VideoCard from "./VideoCard"
import './VideoList.css'

const VideoList = (props) => {

    const onDelete = () => {
        
    }


    return (
        <div className="video__list">            
            {props.videos?.map((video) => (
                <div className="video__list-item">
                <VideoCard key={video.id} video={video} onDelete={onDelete} />
                </div>
            ))}
        </div>
    )
}

export default VideoList