const express = require("express")
const cors = require("cors")
const app = express();


const users = require('./routes/users')
const status = require('./routes/status')
const still = require('./routes/still')
const video = require('./routes/video')
const preview_route = require("./routes/preview")
const pool = require('./db/pool')


app.use(
    cors({
        origin: ["http://localhost:5173"],
    })
);
app.use(express.json())
app.use("/auth", users)
app.use("/api/status", status)
app.use("/api/still", still)
app.use("/api/video", video)
app.use("/api/preview", preview_route)
app.get("/health", (req, res) => {
    res.send("OK")
});

module.exports = app