var fs = require('fs')
var path = require('path')
var Sequelize = require('sequelize')

var db = {}

var sequelize = new Sequelize(process.env.POSTGRES_URL || 'postgresql://postgres:@192.168.99.101:5432/newsletter_service', {
  define: {
    timestamps: false,
    freezeTableName: true
  }
})

fs.readdirSync(__dirname)
  .filter(file => file.indexOf('.') !== 0 && file !== 'index.js')
  .forEach(file => {
    var model = sequelize.import(path.join(__dirname, file))
    db[model.name] = model
  })

Object.keys(db).forEach(function(modelName) {
  if ('associate' in db[modelName]) {
    db[modelName].associate(db)
  }
})

db.sequelize = sequelize

module.exports = db
