var rabbit = require('./rabbit')
var models = require('./models')

var exchange = rabbit.fanout('broadcast')
var eventsQueue = exchange.queue({ durable: true, exclusive: false })

eventsQueue.consume(onMessage, { noAck: true })

function onMessage(msg, ack) {
  console.log('received:', msg);

  switch (msg.type) {
    case 'auth:user:created':
      models.subscriber.create({
        userId: msg.data.user.id
      })
      break
  }

}
