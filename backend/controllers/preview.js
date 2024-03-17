const preview = require('../models/preview')
const stream = require('../stream')


const previewStart = async (req, res) => {
    try {
        const response = await preview.start()
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

const previewStop = async (req, res) => {
    try {
        const response = await preview.stop()
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

const addListener = (req, res) => {
    
    res.writeHead(200, {
        'Content-Type': 'multipart/x-mixed-replace;boundary=FRAME',
        'Age': 0,
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })

    const listener = (frame) => {
        res.write('--FRAME\r\n')
        res.write('Content-Type: image/jpeg\r\n')
        res.write('Content-Length: ' + frame.length + '\r\n')
        res.write("\r\n")
        res.write(Buffer.from(frame, 'binary'))
        res.write("\r\n")
    }

    conn = stream.connection()

    conn.on('connection', (stream) => {
        console.log(stream)
        console.log("Connected to stream.")
    })


    conn.on('data', listener)
    res.on('close', () => {
        console.log("Streaming ended.")
        res.end()
        conn.off('data', listener)        
        conn.end()
        if (conn.listenerCount == 0) {
            preview.stop()
        }
    })
}

module.exports = {
  previewStart, previewStop, addListener
}