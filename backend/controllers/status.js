const status = require('../models/status')
const handleResponse = require('./handle_response')

const getStatus = async (req, res) => handleResponse({res: res, func: status.fetch})



module.exports = {
  getStatus
}