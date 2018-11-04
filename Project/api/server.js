'use strict'

const express = require('express')
const bodyParser = require('body-parser')
const { graphqlExpress } = require('apollo-server-express')
const schema = require('./data/schema')
const jwt = require('express-jwt')
const cors = require('cors')

require('dotenv').config()

const PORT = 3000

// create our express app
const app = express()
app.use(cors())

// auth middleware
const auth = jwt({
  secret: process.env.JWT_SECRET,
  credentialsRequired: false
})

// graphql endpoint
app.use(
  '/graphql',
  bodyParser.json(),
  auth,
  graphqlExpress(req => ({
    schema,
    context: {
      user: req.user
    }
  }))
)

app.listen(PORT, () => {
  console.log(`The server is running on http://localhost:${PORT}/graphql`)
})
