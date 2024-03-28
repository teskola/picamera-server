const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const users = require('../models/users');

const loginUser = async (req, res) => {
    try {
        const { email, password } = req.body;
 
        const user = users.find(email)
     
        if (!user[0]) {
          return res.status(401).json({ message: "Invalid e-mail or password" });
        }
     
        const passwordMatch = await bcrypt.compare(password, user[0].password);
     
        if (!passwordMatch) {
          return res.status(401).json({ message: "Invalid e-mail or password" });
        }
     
        const token = jwt.sign(
          { email: user[0].email },
          process.env.JWT_KEY,
          {
            expiresIn: "1h",
          }
        );
     
        res.json({ message: "Logged in successfully", token });

    } catch (err) {
        console.log(err)
        return res.status(500).send()
    }
}

module.exports = {loginUser}