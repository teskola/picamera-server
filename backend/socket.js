const net = require("net")

const connect = () => {
    return net.connect({
        port: 9090,
        host: 'localhost',
    })
}

module.exports = {connect}