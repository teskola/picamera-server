const pool = require("./db/pool");
const bcrypt = require('bcryptjs');
const Joi = require('joi');

const args = process.argv.slice(2)

const body = { email: args[0], password: args[1] }

const schema = Joi.object({
    email: Joi.string().email().max(255).required(),
    password: Joi.string().min(6).max(72).required(),
});

const { error } = schema.validate(body)

if (error) {
    console.log(error)
    return
}
bcrypt.hash(body.password, 12, (err, hash) => {
    if (err) {
        console.log(err)
        return
    }
    const newUser = { email: body.email, password: hash }

    pool.getConnection((err, connection) => {
        if (err) {
            console.log(err)
            return
        }
        connection.query('INSERT INTO users SET ?;', newUser, (err, result) => {
            if (err) {
                console.log(err)
            } else {
                console.log(result)
            }
            connection.end()
            return
        })
        connection.release()
    })
})


