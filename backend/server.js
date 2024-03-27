const app = require('./app');
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const socket = require("./socket");
const status = require('./models/status');

const io = new Server(server, {
  cors: {
    origin: ["http://localhost:5173"]
  }
});

io.on('connection', async (socket) => {
  socket.emit('status', await status.fetch())
});

const conn = socket.connect()
conn.write(JSON.stringify({ action: 'status_listen' }))
conn.on('data', (stream) => {
  io.emit('status', JSON.parse(stream.toString()))
})

const PORT = 5000;

server.listen(PORT, () => {
  console.log(`Backend is running on port ${PORT}`);
});