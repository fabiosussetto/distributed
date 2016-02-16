var jackrabbit = require('jackrabbit')

module.exports = jackrabbit(process.env.RABBIT_URL || 'amqp://192.168.99.101:5672')
