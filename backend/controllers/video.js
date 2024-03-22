const Joi = require('joi')
const video = require('../models/video')
const { v1 } = require('uuid')
const moment = require('moment');


const videoStart = async (req, res) => {
    console.log('Start received: ' + (moment().format('DD/MM/YYYY HH:mm:ss.SSS')))

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
        action: 'video_start',
        id: v1(),
        resolution: resolution,
        quality: quality
    }

    try {
        const response = await video.start(params)
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

const videoStop = async (req, res) => {
    try {
        const response = await video.stop()
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

const videoUpload = async (req, res) => {

    const { name } = req.body

    try {
        const response = await video.upload(req.params.id, name)
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

const videoDelete = async (req, res) => {
    try {
        const response = await video.delete(req.params.id)
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


module.exports = {
    videoStart,
    videoStop,
    videoUpload,
    videoDelete
}