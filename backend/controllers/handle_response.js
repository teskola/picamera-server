const handleResponse = async ({ res, func, params }) => {
    try {
        const response = await func(params)
        if (response) {
            return res.status(response.error ? 409 : 200).send(response)
        } else {
            throw new Error('Null response.')
        }

    }
    catch (err) {
        console.log(err)
        return res.status(500).send()
    }
}

module.exports = handleResponse