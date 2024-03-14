const net = require("net")

const createConnection = () => {
    return net.createConnection({
        port: 9090,
        host: 'localhost',
    })
}

module.exports = {createConnection}