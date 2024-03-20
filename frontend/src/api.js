

export const startStill = async ({ interval, path, limit, full_res, epoch, delay }) => {
    try {
        const res = await fetch(                      
            `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/still/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                "interval": interval,
                "name": path,
                "limit": limit,
                "full_res": full_res,
                "epoch": epoch,
                "delay": delay
            })
        }
        )        
        return {body: await res.json(), status: res.status}
    }
    catch (err) {
        console.log(err)
        return {status: 500}
    }
}

export const stopStill = async () => {
    try {
        const res = await fetch(
            `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/still/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },        
        }
        )
        return {body: await res.json(), status: res.status}
    }
    catch (err) {
        console.log(err)
        return {status: 500}
    }
    
}

export const startVideo = async ({ resolution, quality }) => {
    try {
        const res = await fetch(
            `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/video/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                "resolution": resolution,
                "quality": quality                
            })
        }
        )
        return {body: await res.json(), status: res.status}
    }
    catch (err) {
        console.log(err)
        return {status: 500}
    }
}

export const stopVideo = async () => {
    try {
        const res = await fetch(
            `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/video/stop/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
        }
        )
        return {body: await res.json(), status: res.status}
    }
    catch (err) {
        console.log(err)
        return {status: 500}
    }
}