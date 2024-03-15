const express = require('express');
const router = express.Router();
const { videoStart, videoStop, videoPause, videoDelete } = require('../controllers/video');


router.post('/start', videoStart)
router.post('/stop', videoStop)
router.post('/pause/:id', videoPause)
router.delete('/:id', videoDelete)

module.exports = router;