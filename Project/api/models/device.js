'use strict';
module.exports = (sequelize, DataTypes) => {
  const Device = sequelize.define('Device', {
    name: DataTypes.STRING,
    userId: DataTypes.INTEGER
  }, {});
  Device.associate = function(models) {
    // associations can be defined here
  };
  return Device;
};