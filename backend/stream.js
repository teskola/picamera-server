const socket = require("./socket")

let instance

const connection = () => {
    if (!instance) {
        console.log('Initializing...')
        instance = createConnection()
    }
    console.log('New connection')
    return instance
}

const createConnection = () => {
    const conn = socket.connect()
    const req = conn.write(JSON.stringify({ action: 'preview_listen' }), (err) => {
        if (err) {
            console.log(err)
            throw new Error(err)
        }
    });
    if (req) {
        console.log('Success')
        return conn
    }
}

module.exports = { connection }