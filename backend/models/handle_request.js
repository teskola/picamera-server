const socket = require('../socket')

const handleRequest = ({action, params = {}}) => new Promise((resolve, reject) => {
    const conn = socket.connect()
    const req = conn.write(JSON.stringify({action, ...params}))
    if (req) {
        conn.once('data', (stream) => resolve(JSON.parse(stream.toString())))
    } else {
        reject('Sending request failed.')
    }
})

module.exports = { handleRequest } 