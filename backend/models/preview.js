const { handleRequest } = require('./handle_request')

const preview = {
    start: () => handleRequest({ action: 'preview_start' }),
    stop: () => handleRequest({ action: 'preview_stop' })
}

module.exports = preview