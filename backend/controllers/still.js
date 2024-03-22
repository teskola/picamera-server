import { object, number, string, boolean } from 'joi'
import { start, stop } from '../models/still'
import handleResponse from './handle_response'


const stillStart = async (req, res) => {

    const { interval, name, limit, full_res, epoch, delay } = req.body
    const schema = object({
        interval: number().integer().min(1).max(60 * 60 * 6).required(),
        name: string().min(1).max(70).required(),
        limit: number().integer().min(0).max(32768).required(),
        full_res: boolean().required(),
        epoch: number().integer().min(Math.floor(Date.now() / 1000)).max(2147483648).optional(),
        delay: number().min(1).max(32768).optional()
    }).xor('epoch', 'delay').options({ abortEarly: false })

    const { error } = schema.validate(req.body)
    if (error) {
        return res.status(400).send({ error: error.details })
    }

    const params = {
        interval: interval,
        name: name,
        limit: limit,
        full_res: full_res,
        epoch: epoch ?? null,
        delay: delay ?? null
    }

    return handleResponse({res: res, func: start, params: params})  

}

const stillStop = async (req, res) => handleResponse({res: res, func: stop})

export default {
    stillStart,
    stillStop
}