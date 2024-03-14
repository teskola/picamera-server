const express = require("express");
const cors = require("cors");
const net = require("net")
const app = express();
const socket = net.createConnection({
    port: 9090,
    host: 'localhost',
}, function () {
    console.log('connected');
})


app.use(
    cors({
        origin: ["http://localhost:5173"],
    })
);
app.use(express.json());
app.get("/health", (req, res) => {
    res.send("OK");
});

module.exports = app;