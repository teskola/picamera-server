const socket = require('../socket')

const getStatus = (req, res) => {
  const connection = socket.createConnection()
  const request = connection.write(JSON.stringify({ action: 'status' }));
  if (request) {
    connection.once('data', (stream) => {
      connection.end()
      return res.send(stream.toString())
    })
  }
  else {
    console.log("Writing status to socket failed")
    return res.status(500).send({ error: 'Something went wrong!' });
  }

}

module.exports = {
  getStatus
}