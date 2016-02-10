var jackrabbit = require('jackrabbit');
var rabbit = jackrabbit(process.env.RABBIT_URL);

var exchange = rabbit.fanout('broadcast');
var eventsQueue = exchange.queue({ durable: true, exclusive: true });


eventsQueue.consume(onMessage, { noAck: true });

function onMessage(data, ack) {
  console.log('received:', data);
}
