const {previewStream} = require('../stream')

const addListener = (req, res) => {

    const listener = (frame) => {
        res.write('--FRAME\r\n')
        res.write('Content-Type: image/jpeg\r\n')
        res.write('Content-Length: ' + frame.length + '\r\n')
        res.write("\r\n")
        res.write(Buffer.from(frame, 'binary'))
        res.write("\r\n")
    }

    res.writeHead(200, {
        'Content-Type': 'multipart/x-mixed-replace;boundary=FRAME',
        'Age': 0,
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })

    previewStream.start(listener)
    res.on('close', () => {
        previewStream.stop(listener)
        res.end()        
    })
}

module.exports = {
    addListener
}