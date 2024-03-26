const app = require('./app');
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server, {
  cors: {
    origin: ["http://192.168.1.129:5000"]
  }
});

io.on('connection', (socket) => {
  console.log('a user connected');
});

const PORT = 5000;

server.listen(PORT, () => {
  console.log(`Backend is running on port ${PORT}`);
});

module.exports = {io}