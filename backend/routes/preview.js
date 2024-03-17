const express = require('express');
const router = express.Router();

const { addListener } = require('../controllers/preview');

router.get('/live.mjpeg', addListener)


module.exports = router;