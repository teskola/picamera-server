const socket = require('../socket')

const getStatus = async (req, res) => {
  try {
    const response = socket.write('status');
    socket.on('data', (stream) => {
      console.log(stream)
    })
    //return res.send(response);

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