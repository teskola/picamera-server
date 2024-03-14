const socket = require('../socket')
const Joi = require('joi')


const stillStart = (req, res) => {

    const { interval, name, limit, full_res, epoch, delay } = req.body
    const schema = Joi.object({
        interval: Joi.number().integer().min(1).max(60 * 60 * 6).required(),
        name: Joi.string().min(1).max(100).required(),
        limit: Joi.number().min(0).integer().required(),
        full_res: Joi.boolean().required(),
        epoch: Joi.number().integer().min(Math.floor(Date.now() / 1000)).optional(),
        delay: Joi.number().min(1).optional()
    }).xor('epoch', 'delay')

    const { error } = schema.validate(req.body)
    if (error) {
        console.log(error.details)
        return res.status(400).send({ error: error.details })
    }

    const action = {
        action: 'still_start',
        interval: interval,
        name: name,
        limit: limit,
        full_res: full_res,
        epoch: epoch,
        delay: delay
    }

    const connection = socket.createConnection()
    const request = connection.write(JSON.stringify(action));
    if (request) {
        connection.once('data', (stream) => {
            connection.end()
            const string = stream.toString()
            const json = JSON.parse(string)
            if (json.error) {                
                return res.status(409).send(string);
            }
            return res.send(string)
        })
    }
    else {
        console.log("Writing still_start to socket failed")
        return res.status(500).send({ error: 'Something went wrong!' });
    }


}

const stillStop = (res) => {
    try {
        const request = socket.write('still_stop');
        if (request) {
            socket.once('data', (stream) => {
                return res.send(stream.toString())
            })
        }
        else {
            const response = {
                OK: false,
                statusCode: 500,
                error: err,
            };
            return res.status(500).send(response);
        }

    } catch (err) {
        console.log(err);
        const response = {
            OK: false,
            statusCode: 500,
            error: err,
        };
        return res.status(500).send(response);
    }
}

module.exports = {
    stillStart,
    stillStop
}