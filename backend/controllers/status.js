const status = require('../models/status')

const getStatus = async (req, res) => {
  try {
    const response = await status.fetch()    
    return res.send(response)
  }
  catch (err) {
    console.log(err)
    return res.status(500).send({ error: 'Something went wrong!' });
  }

}

module.exports = {
  getStatus
}