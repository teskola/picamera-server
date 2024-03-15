const socket = require('../socket')
const connection = socket.createConnection()

const status = {
    fetch: () => new Promise((resolve, reject) => {
        // const connection = socket.createConnection()
        const request = connection.write(JSON.stringify({ action: 'status' }), (err) => {
            if (err) {
                console.log(err)
                reject(err)
            }
        });
        if (request) {
            const listener = (stream) => {
                connection.off('data', listener)
                // connection.end()
                resolve(stream.toString())
            }
            connection.on('data', listener)
        }
        else {
            // connection.end()
            reject("Writing status to socket failed")
        }
    })
}

module.exports = status