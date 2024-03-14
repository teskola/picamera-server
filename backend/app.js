const express = require("express");
const cors = require("cors");
const app = express();
const status = require('./routes/status')

app.use(
    cors({
        origin: ["http://localhost:5173"],
    })
);
app.use(express.json());
app.use("/api/status", status);
app.get("/health", (req, res) => {
    res.send("OK");
});

module.exports = app;