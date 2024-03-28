const mysql = require('mysql2')

const pool = mysql.createPool({
    host: 'localhost',
    user: 'camera',
    database: 'cameradb'
})

pool.getConnection((err, connection) => {
    if (err) {
        console.log(err)
    } else {
        connection.query("CREATE TABLE IF NOT EXISTS users ( email VARCHAR(255) NOT NULL, password VARCHAR(60) NOT NULL, created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (email))", 
        (err, result) => {
            if (err) {
                console.log(err)
            } 
        })
    }
    connection.release()
})

module.exports = pool