'use strict'

const { makeExecutableSchema } = require('graphql-tools')
const resolvers = require('./resolvers')

// Define our schema using the GraphQL schema language
const typeDefs = `
  type User {
    id: Int!
    username: String!
    email: String!
    listenerCommand: String
  }

  type Command {
    id: Int!
    userId: Int!
    from: String!
    to: String!
  }

  type Query {
    me: User
    commands: [Command]
  }

  type Mutation {
    signup (username: String!, email: String!, password: String!): String
    login (email: String!, password: String!): String
    updateCommands (froms: [String]!, tos: [String]!, listenerCommand: String!): [Command]
  }
`

module.exports = makeExecutableSchema({ typeDefs, resolvers })
