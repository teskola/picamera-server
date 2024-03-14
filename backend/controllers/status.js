const socket = require('../socket')

const getStatus = (req, res) => {
  const request = socket.write(JSON.stringify({ action: 'status' }));
  if (request) {
    socket.once('data', (stream) => {
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