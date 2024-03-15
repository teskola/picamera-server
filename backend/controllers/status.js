const status = require('../models/status')

const getStatus = async (req, res) => {
  try {
    const response = await status.fetch()
    if (response) {
      return res.send(response)
    } else {
      throw new Error('Null response.')
    }

  }
  catch (err) {
    console.log(err)
    return res.status(500).send({ error: 'Something went wrong!' })
  }

}

module.exports = {
  getStatus
}