const status = require('../models/status')

const getStatus = async (req, res) => {
  try {
    const response = await status.fetch()
    if (response) {
      console.log(response)
      return res.send(response)
    } else {
      return res.status(500).send({ error: 'Something went wrong!' });
    }

  }
  catch (err) {
    console.log(err)
    return res.status(500).send({ error: 'Something went wrong!' });
  }

}

module.exports = {
  getStatus
}