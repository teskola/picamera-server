const Joi = require('joi')
const video = require('../models/video')
const { v1 } = require('uuid')
const { handleResponse } = require('./handle_response')


const videoStart = async (req, res) => {

    const { resolution, quality } = req.body

    const schema = Joi.object({
        quality: Joi.number().integer().min(1).max(5).required(),
        resolution: Joi.string().valid("720p", "1080p").required()
    })

    const { error } = schema.validate(req.body)

    if (error) {
        return res.status(400).send({ error: error.details })
    }

    const params = {
        id: v1(),
        resolution: resolution,
        quality: quality
    }

    return handleResponse({ res: res, func: video.start, params: params })

}

const videoStop = async (req, res) => handleResponse({ res: res, func: video.stop })

const videoUpload = async (req, res) => {

    const { name } = req.body
    const params = {
        id: req.params.id,
        name: name
    }

    return handleResponse({ res: res, func: video.upload, params: params })

}

const videoDelete = async (req, res) => handleResponse({ res: res, func: video.delete })


module.exports = {
    videoStart,
    videoStop,
    videoUpload,
    videoDelete
}