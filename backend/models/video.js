const socket = require('../socket')
const { requestStream } = require('../stream')

const video = {
    upload: (id, name) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'video_upload', id: id, name: name }))

        if (req) {
            conn.once('data', (stream) => resolve(JSON.parse(stream.toString())))
        }
    }),
    delete: (id) => new Promise( (resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'video_delete', id: id }))
        if (req) {
            conn.once('data', (stream) => resolve(JSON.parse(stream.toString())))
        }
    }),
    stop: () => new Promise(async (resolve, reject) => {
        const conn = await requestStream.getConnection()
        const req = conn.write(JSON.stringify({ action: 'video_stop' }))
        if (req) {
            conn.once('data', (stream) => {
                result = JSON.parse(stream.toString())
                if (result.error) {
                    reject(result)
                }
                else {
                    resolve(result)
                }

            })
        }
    }),
    start: (params) => new Promise(async (resolve, reject) => {        
        console.log('Connect to socket: ' + (moment().format('DD/MM/YYYY HH:mm:ss.SSS')))
        const conn = await socket.connect()
        const req = conn.write(JSON.stringify(params))
        if (req) {
            conn.once('data', (stream) => {
                result = JSON.parse(stream.toString())
                if (result.error) {
                    reject(result)
                }
                else {
                    resolve(result)
                }

            })
        }
    })
}

module.exports = video