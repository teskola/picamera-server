const socket = require('../socket')

const status = {
    fetch: () => new Promise((resolve, reject) => {        
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'status' }) + '\n', (err) => {
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

module.exports = status