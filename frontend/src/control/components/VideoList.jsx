import VideoCard from "./VideoCard"
import './VideoList.css'

const VideoList = (props) => {

    const onDelete = () => {

    }


    return (
        <ul className="video__list">
            {props.videos.length > 0 && props.videos?.map((video) => (
                <li key={video.id} className="video__list-item">
                    <VideoCard video={video} onDelete={onDelete} />
                </li>
            ))}
        </ul>
    )
}

export default VideoList