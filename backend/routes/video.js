const express = require('express');
const router = express.Router();
const { videoStart, videoStop, videoUpload, videoDelete } = require('../controllers/video');


router.post('/start', videoStart)
router.post('/stop/:id', videoStop)
router.post('/upload/:id', videoUpload)
router.delete('/:id', videoDelete)

module.exports = router;