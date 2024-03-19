const socket = require('../socket')

const still = {
    stop: () => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'still_stop' }) + '\n', (err) => {
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
    start: (params) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify(params) + '\n', (err) => {
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

module.exports = still