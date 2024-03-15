const Joi = require('joi')
const video = require('../models/video')


const videoStart = async (req, res) => {

  const { resolution, quality, name } = req.body

  const schema = Joi.object({
    quality: Joi.number().integer().min(1).max(5).required(),
    name: Joi.string().min(1).max(100).required(),
    resolution: Joi.string().valid(["720p", "1080p"]).required()
  })

  const { error } = schema.validate(req.body)

  if (error) {
    console.log(error.details)
    return res.status(400).send({ error: error.details })
  }

  const params = {
    action: 'video_start',
    name: name,
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
    const response = await video.stop()
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
  videoStop
}