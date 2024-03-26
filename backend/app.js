const express = require("express")
const cors = require("cors")
const app = express();
const http = require('http');
const server = http.createServer(app);

const status = require('./routes/status')
const still = require('./routes/still')
const video = require('./routes/video')
const preview_route = require("./routes/preview")
const status_listener = require('./status_listener')

const PORT = 5000;

app.use(
    cors({
        origin: ["http://localhost:5173"],
    })
);
app.use(express.json())
app.use("/api/status", status)
app.use("/api/still", still)
app.use("/api/video", video)
app.use("/api/preview", preview_route)
app.get("/health", (req, res) => {
    res.send("OK")
});

server.listen(PORT, () => {
    console.log(`Backend is running on port ${PORT}`);
  });