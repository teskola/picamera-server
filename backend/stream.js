const socket = require("./socket")

let instance

const connection = () => {
    if (!instance) {
        instance = connect()
    }
    return instance
}

const connect = () => {
    const conn = socket.connect()
    const req = conn.write(JSON.stringify({ action: 'preview_listen' }), (err) => {
        if (err) {
            throw new Error(err)
        }
    });
    if (req) {
        return conn
    }
}

module.exports = { connection }