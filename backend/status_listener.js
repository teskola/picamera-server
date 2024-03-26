const socket = require("./socket")

class StatusListener {
    constructor() {
        this.connection = this.#createConnection()
        this.connection.on('data', (stream) => {
            console.log(stream.toString())
        })
    }

    #createConnection = () => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'status_listen' }), (err) => {
            if (err) {
                console.log(err)
                throw new Error(err)
            }
        });
        if (req) {
            console.log('Listening to camera status.')
            return conn
        }
    }

    
    
}

const status_listener = new StatusListener()


module.exports = status_listener 