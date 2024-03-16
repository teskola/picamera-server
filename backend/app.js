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
    res.setHeader('Age', 0)
    res.setHeader('Cache-Control', 'no-cache, private')
    res.setHeader('Pragma', 'no-cache')
    res.setHeader('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
    const listener = (frame) => {
        res.setHeader('Content-Type', 'image/jpeg')
        res.setHeader('Content-Length', Object.keys(frame).length)
        res.write(Buffer.from('--FRAME\r\n') + frame + Buffer.from('\r\n'))
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