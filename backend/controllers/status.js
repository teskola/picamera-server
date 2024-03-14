const socket = require('../socket')

const getStatus = async (req, res) => {
    try {
        const response = socket.write('status');
        if (response.length === 1) {
          return res.send(response[0]);
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