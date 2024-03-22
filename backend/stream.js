const preview = require("./models/preview")
const socket = require("./socket")

class RequestStream {
    constructor() {
        this.socket = []
        this.#addConnection()
    }
    #addConnection = async () => {
        this.socket.push(await socket.connect())
        console.log('New request socket created.')
    }

    getConnection = async () => {
        if (this.socket.length > 0) {
            this.#addConnection()
            return this.socket.pop()
        } 
        console.log('Socket is in use, create a new socket.')
        return await socket.connect()
    }
}

class PreviewStream {
    constructor() {
        this.connection = this.#createConnection()
    }

    #createConnection = async () => {
        const conn = await socket.connect()
        const req = conn.write(JSON.stringify({ action: 'preview_listen' }), (err) => {
            if (err) {
                console.log(err)
                throw new Error(err)
            }
        });
        if (req) {
            console.log('Listening preview stream.')
            return conn
        }
    }

    start = (listener) => {
        preview.start()
        this.connection.on('data', listener)
    }

    stop = (listener) => {

        this.connection.off('data', listener)
        if (this.connection.listenerCount() == 0) {
            preview.stop()
        }

    }
}

const previewStream = new PreviewStream()
const requestStream = new RequestStream()


module.exports = {previewStream, requestStream} 