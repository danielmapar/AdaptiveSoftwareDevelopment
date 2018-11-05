'use strict'

const express = require('express')
const bodyParser = require('body-parser')
const { graphqlExpress } = require('apollo-server-express')
const schema = require('./data/schema')
const jwt = require('express-jwt')
const cors = require('cors')
const huejay = require('huejay')

require('dotenv').config()

const PORT = 3000

// create our express app
const app = express()
app.use(cors())

// Philips Hue config
huejay.discover().then(bridges => {

  console.log("Started Philips Hue config!")

  for (let bridge of bridges) {
    console.log(`Id: ${bridge.id}, IP: ${bridge.ip}`);
  }

  let client = new huejay.Client({
    host: bridges[0].ip,
    username: 'IGPBxiLLsCmI4bHSEH0P0KGsoRKeK4kI8Olswnup'
  })

  client.bridge.ping().then(() => {
    console.log('Successful connection to Philips Bridge');

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
          user: req.user,
          philipsHueClient: client
        }
      }))
    )

    app.listen(PORT, () => {
      console.log(`The server is running on http://localhost:${PORT}/graphql`)
    })

  }).catch(err => {
    console.log("Connection error with Philips Bridge!");
  })
})
