const preview = require("./models/preview")
const socket = require("./socket")

let instance

const connection = () => {
    if (!instance) {
        instance = createConnection()
        preview.start()
    }
    return instance
}

const close = () => {
    preview.stop()
    if (instance) {        
        instance.end()
        instance = null
    }
}

const start = (listener) => {
    const conn = connection()
    conn.on('data', listener)
}

const stop = (listener) => {
    if (instance) {
        instance.off('data', listener)
        if (instance.listenerCount() == 0) {
            close()
        }
    }
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
        return conn
    }
}

module.exports = { start, stop }