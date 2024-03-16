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
    console.log("Streaming started.")
    res.writeHead(200, {
        'Content-Type': 'multipart/x-mixed-replace;boundary=FRAME',
        'Connection': 'keep-alive',
        'Expires': 'Fri, 27 May 1977 00:00:00 GMT',
        'Cache-Control': 'no-cache, no-store, max-age=0, must-revalidate',
        'Pragma': 'no-cache'
    })

    const listener = (frame) => {
        res.write('--FRAME\r\n')
        res.write('Content-Type: image/jpeg\r\n')
        res.write('Content-Length: ' + frame.length + '\r\n')
        res.write("\r\n")
        res.write(Buffer.from(frame, 'binary'))
        res.write("\r\n")
    }
    try {
        connection.on('data', listener)
        res.on('close', () => {
            console.log("Streaming ended.")
            res.end()
        })

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