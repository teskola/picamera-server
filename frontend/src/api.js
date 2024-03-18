export const startStill = async ({ interval, path, limit, full_res, epoch, delay }) => {
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
    return res.json()
}

export const stopStill = async () => {
    const res = await fetch(
        `http://${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api/still/stop`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },        
    }
    )
    return res.json()
}