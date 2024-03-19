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
            conn.once('data', (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            })
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
            conn.once('data', (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            })
        }
    })
}

module.exports = preview