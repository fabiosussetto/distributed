import os
from kombu import Connection, Queue

from .api import db, User

RABBIT_URL = os.environ.get('RABBIT_URL', 'amqp://192.168.99.101:5672')

rpc_queue = Queue(name='rpc', durable=False, no_ack=True)


with Connection(RABBIT_URL) as conn:
    producer = conn.Producer()

    def process_msg(body, message):
        print('Received: {}'.format(body))
        if body.get('resource') == 'user':
            users = db.session.query(User).filter(User.id.in_(body['ids']))
            data = [u.asdict() for u in users]

            producer.publish(data, routing_key=message.properties['reply_to'],
                             correlation_id=message.properties.get('correlation_id'))

    with conn.Consumer(rpc_queue, callbacks=[process_msg]) as consumer:
        while True:
            conn.drain_events()
