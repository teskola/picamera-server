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
app.get("/frame", (req, res) => {

    const connection = socket.createConnection()
    connection.write(JSON.stringify({ action: 'stream' }), (err) => {
        if (err) {
            console.log(err)
            res.status(500).send({ error: 'Something went wrong!' })
        }
    });
    const listener = (frame) => {
        connection.off('data', listener)
        connection.end()
        res.contentType('image/jpeg');
        res.send(Buffer.from(frame, 'binary'))
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
        'Cache-Control': 'no-cache, private',
        'Pragma': 'no-cache',
        'Content-Type': 'multipart/x-mixed-replace; boundary=FRAME'
    })
    const listener = (frame) => {
        res.contentType('image/jpeg');
        res.send(Buffer.from(frame, 'binary'))
        /* res.write(Buffer.from('--FRAME\r\n', 'binary'))
        res.write('Content-Type: image/jpeg\r\n')
        res.write('Content-Length: ' + Object.keys(frame).length)
        res.write("\r\n")
        res.write(Buffer.from(frame, 'binary'))
        res.write(Buffer.from("\r\n", 'binary')) */
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