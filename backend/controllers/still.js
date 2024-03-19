const Joi = require('joi')
const still = require('../models/still')


const stillStart = async (req, res) => {

    const { interval, name, limit, full_res, epoch, delay } = req.body
    const schema = Joi.object({
        interval: Joi.number().integer().min(1).max(60 * 60 * 6).required(),
        name: Joi.string().min(1).max(70).required(),
        limit: Joi.number().integer().min(0).max(32768).required(),
        full_res: Joi.boolean().required(),
        epoch: Joi.number().integer().min(Math.floor(Date.now() / 1000)).max(2147483648).optional(),
        delay: Joi.number().min(1).max(32768).optional()
    }).xor('epoch', 'delay').options({ abortEarly: false })

    const { error } = schema.validate(req.body)
    if (error) {
        return res.status(400).send({ error: error.details })
    }


    const params = {
        action: 'still_start',
        interval: interval,
        name: name,
        limit: limit,
        full_res: full_res,
        epoch: epoch ?? null,
        delay: delay ?? null
    }

    try {
        const response = await still.start(params)
        console.log('response:' + response)
        if (response) {
            return res.send(response)
        } else {
            throw new Error('Null response.')
        }

    }
    catch (response) {
        if (response.error?.running_error) {
            return res.status(409).send(response)
        }
        else {
            console.log(response)
            return res.status(500).send()
        }
    }

    
}

const stillStop = async (req, res) => {
    try {
        const response = await still.stop()
        if (response) {
            if (response.error) {
                return res.status(409).send(response)
            }
            return res.send(response)
        } else {
            throw new Error('Null response.')
        }

    }
    catch (err) {
        console.log(err)
        return res.status(500).send()
    }
}

module.exports = {
    stillStart,
    stillStop
}