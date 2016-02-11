var express = require('express')
var responseTime = require('response-time')

var models = require('./models')
var rabbit = require('./rabbit')

var app = express()
app.use(responseTime())

var exchange = rabbit.default()
var rpc = exchange.queue({name: 'rpc', prefetch: 1, durable: false, noAck: true})

app.get('/', (req, res) => {
  models.subscriber.findAll({ raw: true })
    .then(subscribers => {
      var userIds = subscribers.map(s => parseInt(s.userId))
      exchange.publish({ resource : 'user', ids: userIds }, { key: 'rpc', reply: users => {
        var data = subscribers.map(s => Object.assign({}, s, { user: users.find(u => u.id === parseInt(s.userId)) }))
        res.json(data)
      }})
    })

})

models.sequelize.sync({ force: false }).then(() => {
  app.listen(3000, () => {
    console.log('Newsletter service listening on port 3000...')
  })
})
