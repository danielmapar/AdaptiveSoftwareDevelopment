'use strict';
module.exports = (sequelize, DataTypes) => {
  const CommandHistory = sequelize.define('CommandHistory', {
    userId: DataTypes.INTEGER,
    commandId: DataTypes.INTEGER
  }, {});
  CommandHistory.associate = function(models) {
    CommandHistory.belongsTo(models.Command);
  };
  return CommandHistory;
};
