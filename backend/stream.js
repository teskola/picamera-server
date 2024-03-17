const stream = require("./models/preview")

const connection = stream.listen()

module.exports = {connection}