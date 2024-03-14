const net = require("net")

const socket = net.createConnection({
    port: 9090,
    host: 'localhost',
}, function () {
    console.log('Connected to Camera.');
})

module.exports = socket