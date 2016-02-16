var rabbit = require('./rabbit')

var exchange = rabbit.default();
var rpc = exchange.queue({ name: 'dispatcher_rpc', prefetch: 1, durable: false, noAck: true });

var hookMap = {
  'newsletter:before_listSubscribers': [
    'auth:isLogged',
    'permission:check'
  ]
}

function call (service, method) {
  return new Promise((resolve, reject) => {
    exchange.publish({ method: method }, {
      key: service + '_rpc',
      reply: resolve
    })
  })
}

function processHooks (hooks) {
  return new Promise ((resolve, reject) => {
    function doStep (index) {
      var step = hooks[index]
      var pieces = step.split(':')

      console.log('doStep', index, pieces)
      call(pieces[0], pieces[1])
        .then(resp => {
          console.log('resp', resp, pieces)
          if (index === hooks.length - 1) {
            resolve({ should_continue: true })
            return
          }
          if (resp.should_continue === false) {
            console.log('chain stopped by ', pieces)
            resolve({ should_continue: false })
            return
          }

          doStep(index + 1)
        })
    }

    doStep(0)
  })
}

rpc.consume(onMessage)

function onMessage(data, reply) {
  console.log('got request:', data);
  var hooks = hookMap[data.event]
  if (hooks) {
    processHooks(hooks)
      .then(() => {
        reply({done: true})
      })
  } else {
    console.log('No hooks registered!')
  }
}
