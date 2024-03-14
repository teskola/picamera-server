const socket = require('../socket')

const stillStart = (req, res) => {
  try {
    const request = socket.write('status');
    if (request) {
      socket.once('data', (stream) => {
        const string = stream.toString()
        const json = JSON.parse(string)
        if (json.error) {
            const response = {
                OK: false,
                statusCode: 500,
                error: json.error,
              };
              return res.status(500).send(response);
        }
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

const stillStop = (res) => {
    try {
      const request = socket.write('still_stop');
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
  stillStart,
  stillStop
}