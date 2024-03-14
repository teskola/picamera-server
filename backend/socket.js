const net = require("net")

const createConnection = () => {
    return net.createConnection({
        port: 9090,
        host: 'localhost',
    }, function () {
        console.log('Connected to Camera.');
    })
}

module.exports = {createConnection}