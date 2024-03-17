const socket = require('../socket')

const preview = {
    start: () => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'preview_start' }), (err) => {
            if (err) {
                reject(err)
            }
        });
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
        const req = conn.write(JSON.stringify({ action: 'preview_stop' }), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            }
            conn.on('data', listener)
        }
    })
}

module.exports = preview