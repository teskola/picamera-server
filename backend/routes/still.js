const express = require('express');
const router = express.Router();
const { stillStart, stillStop } = require('../controllers/still');

router.post('/start', stillStart);
router.post('/stop', stillStop)

module.exports = router;