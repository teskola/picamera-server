const preview = require("./models/preview")
const socket = require("./socket")

class Stream {
    constructor() {
        console.log('Constructor called.')
        this.connection = this.#createConnection()
    }

    #createConnection = () => {
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

    start = (listener) => {
        this.connection.on('data', listener)
    }

    stop = (listener) => {

        this.connection.off('data', listener)
        if (this.connection.listenerCount() == 0) {
            preview.stop()
        }

    }
}

const stream = new Stream()


module.exports =  stream 