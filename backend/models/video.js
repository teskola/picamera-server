const socket = require('../socket')

const video = {
    pause: () => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify({ action: 'video_pause' }), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (request) {
            const listener = (stream) => {
                connection.off('data', listener)
                connection.end()
                resolve(JSON.parse(stream.toString()))
            }
            connection.on('data', listener)
        }
    }),
    delete: (params) => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify(params), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (request) {
            const listener = (stream) => {
                connection.off('data', listener)
                connection.end()
                resolve(JSON.parse(stream.toString()))
            }
            connection.on('data', listener)
        }
    }),
    stop: () => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify({ action: 'video_stop' }), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (request) {
            const listener = (stream) => {
                connection.off('data', listener)
                connection.end()
                resolve(JSON.parse(stream.toString()))
            }
            connection.on('data', listener)
        }
    }),
    start: (params) => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify(params), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (request) {
            const listener = (stream) => {
                connection.off('data', listener)
                connection.end()
                resolve(JSON.parse(stream.toString()))
            }
            connection.on('data', listener)
        }
    })
}

module.exports = video