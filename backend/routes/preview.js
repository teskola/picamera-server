const express = require('express');
const router = express.Router();

const { previewStart, previewStop } = require('../controllers/preview');

router.get('/live.mjpeg', getStatus)
router.patch('/start', previewStart)
router.patch('/stop', previewStop)

module.exports = router;