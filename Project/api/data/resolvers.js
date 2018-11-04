'use strict'

const { User, Command } = require('../models')
const bcrypt = require('bcrypt')
const jsonwebtoken = require('jsonwebtoken')
require('dotenv').config()

const resolvers = {
  Query: {
    // fetch the profile of currenly athenticated user
    async me (_, args, { user }) {
      // Make sure user is logged in
      if (!user) {
        throw new Error('You are not authenticated!')
      }

      // user is authenticated
      return await User.findById(user.id)
    },

    // fetch the commands of currenly athenticated user
    async commands (_, args, { user }) {
      // Make sure user is logged in
      if (!user) {
        throw new Error('You are not authenticated!')
      }

      return await Command.findAll({
        where: {
          userId: user.id
        }
      });
    }
  },

  Mutation: {
    // Handle user signup
    async signup (_, { username, email, password }) {
      const user = await User.create({
        username,
        email,
        password: await bcrypt.hash(password, 10)
      })

      // Return json web token
      return jsonwebtoken.sign(
        { id: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: '1y' }
      );
    },

    // Handles user login
    async login (_, { email, password }) {
      const user = await User.findOne({ where: { email } })

      if (!user) {
        throw new Error('No user with that email')
      }

      const valid = await bcrypt.compare(password, user.password)

      if (!valid) {
        throw new Error('Incorrect password')
      }

      // Return json web token
      return jsonwebtoken.sign(
        { id: user.id, email: user.email },
        process.env.JWT_SECRET,
        { expiresIn: '1y' }
      )
    },

    async updateCommands (_, { froms, tos, listenerCommand }, { user }) {

      // Make sure user is logged in
      if (!user) {
        throw new Error('You are not authenticated!')
      }

      if (!listenerCommand) {
        throw new Error('Listener command must not be null!')
      }

      if (!froms || !tos || froms.length !== tos.length) {
        throw new Error('From and to must have same size!')
      }

      await Command.destroy({
        where: {
          userId: user.id
        }
      });

      for (let i = 0; i < froms.length; i++) {
        const from = froms[i];
        const to = tos[i];

        await Command.create({
          userId: user.id,
          from,
          to,
        });
      }

      await User.update(
        {
          listenerCommand
        },
        {
          where: {
            id: user.id
          }
        }
      );

      return await Command.findAll({
        where: {
          userId: user.id
        }
      });
    }
  }
}

module.exports = resolvers
