const pool = require("./db/pool");
const bcrypt = require('bcryptjs');
const Joi = require('joi');

async function main () {
    const args = process.argv.slice(2)

    const body = { email: args[0], password: args[1] }

    const schema = Joi.object({
        email: Joi.string().email().max(255).required(),
        password: Joi.string().min(6).max(72).required(),
    });

    const { error } = schema.validate(body)

    if (error) {        
        return error
    }

    bcrypt.hash(body.password, 12, (err, hash) => {
        if (err) {
            return err
        }
        const newUser = { email: body.email, password: hash }
        pool.getConnection((err, connection) => {
            if (err) {
                return err
            }
            connection.query('INSERT INTO users SET ?;', newUser, (err, result) => {
                if (err) {
                    return err
                } else {
                    return result
                }
            })
            connection.release()
        })
    })
}

const result = await main()

console.log(result)




