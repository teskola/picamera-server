const { handleRequest } = require('./handle_request')

const status = {
    fetch: () => handleRequest({action: 'status'})
}

module.exports = status