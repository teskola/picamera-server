const mysql = require('mysql2')

const pool = mysql.createPool({
    host: 'localhost',
    user: 'camera',
    database: 'cameradb'
})

module.exports = pool