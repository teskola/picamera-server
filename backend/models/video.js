const socket = require('../socket')

const video = {
    upload: (id) => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify({ action: 'video_upload', id: id }), (err) => {
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
    delete: (id) => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify({action: 'video_delete', id: id}), (err) => {
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
    stop: (id) => new Promise((resolve, reject) => {
        const connection = socket.createConnection()
        const request = connection.write(JSON.stringify({ action: 'video_stop', id: id }), (err) => {
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