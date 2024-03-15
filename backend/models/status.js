const socket = require('../socket')

const status = {
    fetch: () => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify({ action: 'statu' }), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (request) {
            const listener = (stream) => {
                connection.off('data', listener)
                connection.end()
                resolve(JSON.parse(stream.toString()))
            }
            connection.on('data', listener)
        }
    })
}

module.exports = status