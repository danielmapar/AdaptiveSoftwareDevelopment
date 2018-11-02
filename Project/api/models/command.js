'use strict';
module.exports = (sequelize, DataTypes) => {
  const Command = sequelize.define('Command', {
    deviceId: DataTypes.INTEGER,
    userId: DataTypes.INTEGER,
    from: DataTypes.STRING,
    to: DataTypes.STRING
  }, {});
  Command.associate = function(models) {
    // associations can be defined here
  };
  return Command;
};