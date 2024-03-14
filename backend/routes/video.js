const express = require('express');
const router = express.Router();
const { videoStart, videoStop } = require('../controllers/video');


router.post('/start', videoStart);
router.post('/stop', videoStop)

module.exports = router;