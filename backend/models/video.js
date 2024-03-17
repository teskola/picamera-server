const socket = require('../socket')

const video = {
    upload: (id, name) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'video_upload', id: id, name: name}), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            }
            conn.on('data', listener)
        }
    }),
    delete: (id) => new Promise((resolve, reject) => {
        const conm = socket.connect()
        const req = conm.write(JSON.stringify({action: 'video_delete', id: id}), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (req) {
            const listener = (stream) => {
                conm.off('data', listener)
                conm.end()
                resolve(JSON.parse(stream.toString()))
            }
            conm.on('data', listener)
        }
    }),
    stop: (id) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify({ action: 'video_stop', id: id }), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            }
            conn.on('data', listener)
        }
    }),
    start: (params) => new Promise((resolve, reject) => {
        const conn = socket.connect()
        const req = conn.write(JSON.stringify(params), (err) => {
            if (err) {
                reject(err)
            }
        });
        if (req) {
            const listener = (stream) => {
                conn.off('data', listener)
                conn.end()
                resolve(JSON.parse(stream.toString()))
            }
            conn.on('data', listener)
        }
    })
}

module.exports = video