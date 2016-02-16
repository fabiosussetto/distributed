var express = require('express')
var responseTime = require('response-time')

var models = require('./models')
var rabbit = require('./rabbit')

var app = express()
app.use(responseTime())

var exchange = rabbit.default()
var rpc = exchange.queue({name: 'dispatcher_rpc', prefetch: 1, durable: false, noAck: true})

function callService (msg) {
  return new Promise((resolve, reject) => {
    exchange.publish(msg, { key: 'dispatcher_rpc', reply: resolve })
  })
}

function toArgs () {
  return (arguments.length === 1?[arguments[0]]:Array.apply(null, arguments));
}

function createServiceApi (id) {
  const serviceId = id
  const methods = {}

  function register (name, fn) {
    methods[name] = fn
  }

  function call (name, ...args) {
    return callService({ event: `${serviceId}:before_${name}` })
      .then(checkRes => {
        args.push(checkRes)
        return methods[name].apply(this, args)
      })
  }

  return {
    register,
    call
  }
}

const serviceApi = createServiceApi('newsletter')

serviceApi.register('listSubscribers', function (checkRes) {
  console.log('AA', checkRes)
  return models.subscriber.findAll({ raw: true })
    .then(subscribers => {
      return subscribers.map(s => parseInt(s.userId))
    })
})


app.get('/', (req, res) => {
  console.log('api called')
  serviceApi.call('listSubscribers')
    .then(subs => {
      res.json(subs)
    })

  //callService({ event: 'newsletter:beforeFetch', context: { userId: 1 } })
  //  .then(checkRes => {
  //    console.log('RESP', checkRes)
  //    if (!checkRes.should_continue) {
  //      res.json({ should_continue: false })
  //      return
  //    }
  //
  //    models.subscriber.findAll({ raw: true })
  //      .then(subscribers => {
  //        var userIds = subscribers.map(s => parseInt(s.userId))
  //        res.json(userIds)
  //        //callService({ resource : 'user', ids: userIds })
  //        //  .then(users => {
  //        //    var data = subscribers.map(s => Object.assign({}, s, { user: users.find(u => u.id === parseInt(s.userId)) }))
  //        //    res.json(data)
  //        //  })
  //      })
  //  })
})

models.sequelize.sync({ force: false }).then(() => {
  app.listen(3000, () => {
    console.log('Newsletter service listening on port 3000...')
  })
})
