const { handleRequest } = require('./handle_request')


const video = {
    upload: (params) => handleRequest({ action: 'video_upload', params: params }),
    delete: (params) => handleRequest({ action: 'video_delete', params: params }),
    stop: () => handleRequest({ action: 'video_stop' }),
    start: (params) => handleRequest({ action: 'video_start', params: params })
}

module.exports = video