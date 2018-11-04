'use strict';
module.exports = (sequelize, DataTypes) => {
  const User = sequelize.define('User', {
    username: DataTypes.STRING,
    email: DataTypes.STRING,
    password: DataTypes.STRING,
    listenerCommand: DataTypes.STRING
  }, {
    classMethods: {
        associate: function(models) {
          User.hasMany(models.Command);
      }
    }
  });
  return User;
};
