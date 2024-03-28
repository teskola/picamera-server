const pool = require("../db/pool");

const users = {
    find: (email) => new Promise((resolve, reject) => {
        pool.getConnection((err, connection) => {
            if (err) {
                reject(err)
            }
            connection.query("SELECT * FROM users WHERE email LIKE ?", email, (err, result) => {
                if (err) {
                    return reject(err)
                }
                resolve(result)
            })
            connection.release()
        })
    })
}

module.exports = users