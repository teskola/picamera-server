const app = require('./app');
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const socket = require("./socket")

const io = new Server(server, {
  cors: {
    origin: ["http://192.168.1.129:5000"]
  }
});

io.on('connection', (socket) => {
  console.log('a user connected');
});

const conn = socket.connect()
conn.write(JSON.stringify({ action: 'status_listen' }))
conn.on('data', (stream) => {
  io.emit('status', stream.toJSON())
})

const PORT = 5000;

server.listen(PORT, () => {
  console.log(`Backend is running on port ${PORT}`);
});