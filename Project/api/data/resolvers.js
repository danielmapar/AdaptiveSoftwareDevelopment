'use strict'

const { User, Command, CommandHistory } = require('../models')
const bcrypt = require('bcrypt')
const jsonwebtoken = require('jsonwebtoken')
const moment = require('moment')

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

      if (await User.findOne({ where: { email } })) {
        throw new Error('User already registered with this email')
      }

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
    },

    async sendCommand (_, { fromCommand }, { user, philipsHueClient }) {
      if (!user) {
        throw new Error('No user with that email')
      }

      if (!philipsHueClient.lights){
        throw new Error('Philips Hue not connected!')
      }

      const lights = await philipsHueClient.lights.getAll(); //).find(light => light.uniqueId === '00:17:88:01:03:89:c2:2f-0b' );

      const command = await Command.findOne({
        where: {
          userId: user.id,
          from: fromCommand
        }
      });
      if (!command) return "Failed to find command!";

      await CommandHistory.create({
        userId: user.id,
        commandId: command.id,
      });

      const now = new Date()

      const commandsHistory = await CommandHistory.findAll({
          where: {
              userId: user.id,
              createdAt: {
                  $gte: moment(now).subtract(1, "minutes").toDate(),
                  $lte: now
              }
          },
          include: [{
            model: Command
          }]
      });

      const commandsHistoryMap = {};

      // Create a map with previously executed commands in the last minute
      commandsHistory.forEach(commandHistory => {
        const nameValue = commandHistory.Command.to.replace(/ /g,'').split("=")
        if (!commandsHistoryMap[nameValue[0]]) {
          commandsHistoryMap[nameValue[0]] = {}
        }
        if (!commandsHistoryMap[nameValue[0]][nameValue[1]]) {
          commandsHistoryMap[nameValue[0]][nameValue[1]] = 0;
        }
        commandsHistoryMap[nameValue[0]][nameValue[1]] += 1
      });

      const nameValue = command.to.replace(/ /g,'').split("=")

      // Check if the command being executed has a number, otherwise do not balance it
      /*if (!isNaN(nameValue[1])) {
        let total = 0;
        console.log(commandsHistoryMap[nameValue[0]])
        Object.keys(commandsHistoryMap[nameValue[0]]).forEach(val => {
          total += Number(val) *
        });
        total = total / Object.keys(commandsHistoryMap[nameValue[0]]).length;
        eval('light.'+nameValue[0]+'='+total)
      } else {*/
      lights.forEach((light, index) => eval('lights['+index+'].'+command.to))
      //}

      await philipsHueClient.lights.save(lights);

      return "Command executed!";
    },
  }
}

module.exports = resolvers
