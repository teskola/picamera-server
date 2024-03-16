const Joi = require('joi')
const video = require('../models/video')
const {v1} = require('uuid')


const videoStart = async (req, res) => {

  const { resolution, quality } = req.body

  const schema = Joi.object({
    quality: Joi.number().integer().min(1).max(5).required(),
    resolution: Joi.string().valid("720p", "1080p").required()
  })

  const { error } = schema.validate(req.body)

  if (error) {
    console.log(error.details)
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
    return res.status(500).send({ error: 'Something went wrong!' })
  }
}

const videoStop = async (req, res) => {
  try {
    const response = await video.stop(req.params.id)
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

const videoUpload = async (req, res) => {
  try {
    const response = await video.upload(req.params.id)
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

const videoDelete = async (req, res) => {
  try {
    const response = await video.delete()
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


module.exports = {
  videoStart,
  videoStop,
  videoUpload,
  videoDelete
}