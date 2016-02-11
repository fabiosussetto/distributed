module.exports = function(sequelize, DataTypes) {
  return sequelize.define('subscriber', {
    id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
    subscribedAt: { type: DataTypes.DATE, defaultValue: DataTypes.NOW, field: 'subscribed_at' },
    userId: { type: DataTypes.STRING, field: 'user_id' }
  })
}

