const socket = require('../socket')

const getStatus = (req, res) => {
  try {
    const request = socket.write(JSON.stringify({action: 'status'}));
    if (request) {
      socket.once('data', (stream) => {
        return res.send(stream.toString())
      })
    }
    else {
      const response = {
        OK: false,
        statusCode: 500,
        error: err,
      };
      return res.status(500).send(response);
    }    

  } catch (err) {
    console.log(err);
    const response = {
      OK: false,
      statusCode: 500,
      error: err,
    };
    return res.status(500).send(response);
  }
}

module.exports = {
  getStatus
}