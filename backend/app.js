const express = require("express");
const cors = require("cors");
const app = express();
const status = require('./routes/status')
const still = require('./routes/still')
const video = require('./routes/video')
const socket = require('./socket')


app.use(
    cors({
        origin: ["http://localhost:5173"],
    })
);
app.use(express.json())
app.use("/api/status", status)
app.use("/api/still", still)
app.use("/api/video", video)
app.get("/stream", (req, res) => {
    const connection = socket.createConnection()
    connection.write(JSON.stringify({ action: 'stream' }), (err) => {
        if (err) {
            console.log(err)
            res.status(500).send({ error: 'Something went wrong!' })
        }
    });
    res.status(200)
    res.set({
        'Age': 0,
        'Cahce-Control': 'no-cache, private',
        'Pragma': 'no-cache',
        'Content-Type': 'multipart/x-mixed-replace; boundary=FRAME'
    })
    const listener = (frame) => {
        res.set({ 'Content-Type': 'image/jpeg' }, 'Content-Length', Object.keys(frame).length)
        res.send(Buffer.from('--FRAME\r\n'))
        res.send(frame)
        res.send(Buffer.from('\r\n'))
    }
    try {
        connection.on('data', listener)

    } catch (err) {
        console.log('Streaming ended:')
        console.log(err)
        connection.off('data', listener)
        connection.end()
    }


})
app.get("/health", (req, res) => {
    res.send("OK")
});

module.exports = app;