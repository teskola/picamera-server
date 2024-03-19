const socket = require('../socket')

const still = {
    stop: () => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'still_stop' }))
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

module.exports = still