const { handleRequest } = require('./handle_request')

const still = {
    stop: () => handleRequest({ action: 'still_stop' }),
    start: (params) => handleRequest({ action: 'still_start', params: params })
}

module.exports = still