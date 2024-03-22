const net = require("net")
const { resolve } = require("path")

const connect = () => {
    return new Promise((resolve, reject) => {
        resolve(net.connect({
            port: 9090,
            host: 'localhost',
        }))
    })
}

module.exports = { connect }