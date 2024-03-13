export const startStill = async ({ interval, path, limit, full_res, epoch, delay }) => {
    const res = await fetch(
        `${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            "action": "still_start",
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
        `${import.meta.env.VITE_RASPBERRY_URL}:${import.meta.env.VITE_PORT}/api`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            "action": "still_stop"
        })
    }
    )
    return res.json()
}