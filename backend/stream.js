const socket = require("./socket")

let instance

const socket = () => {
    if (!instance) {
        console.log('New connection')
        instance = createConnection()
    }
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

module.exports = { socket }