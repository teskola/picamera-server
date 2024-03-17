const express = require('express');
const router = express.Router();

const { previewStart, previewStop, addListener } = require('../controllers/preview');

router.get('/live.mjpeg', addListener)
router.patch('/start', previewStart)
router.patch('/stop', previewStop)

module.exports = router;