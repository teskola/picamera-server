const socket = require('../socket')

const video = {
    upload: (id, name) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'video_upload', id: id, name: name }))

        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            }
            conn.on('data', listener)
        }
    }),
    delete: (id) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'video_delete', id: id }))

        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            }
            conn.on('data', listener)
        }
    }),
    stop: () => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'video_stop'}))

        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                result = JSON.parse(stream.toString())
                if (result.error) {
                    reject(result)
                }
                else {
                    resolve(result)
                }
            }
            conn.on('data', listener)
        }
    }),
    start: (params) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify(params))
        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                result = JSON.parse(stream.toString())
                if (result.error) {
                    reject(result)
                }
                else {
                    resolve(result)
                }
            }
            conn.on('data', listener)
        }
    })
}

module.exports = video