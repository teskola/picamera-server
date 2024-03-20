const socket = require('../socket')

const still = {
    stop: () => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'still_stop' }))
        if (req) {
            conn.once('data', (stream) => {                
                result = JSON.parse(stream.toString())
                if (result.error) {
                    reject(result)
                }
                else {
                    resolve(result)
                }
            })
        }
    }),
    start: (params) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify(params))
        if (req) {
            conn.once('data', (stream) => {                
                result = JSON.parse(stream.toString())
                if (result.error) {
                    reject(result)
                }
                else {
                    resolve(result)
                }
            })
        }
    })

}

module.exports = still