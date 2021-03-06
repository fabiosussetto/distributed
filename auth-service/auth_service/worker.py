import os
from kombu import Connection, Queue

from .api import db, User

RABBIT_URL = os.environ.get('RABBIT_URL', 'amqp://192.168.99.101:5672')

rpc_queue = Queue(name='auth_rpc', durable=False, no_ack=True)


def is_logged(data):
    print('is_logged called!', data)
    return dict(should_continue=True)


actions = {
    'isLogged': is_logged
}


with Connection(RABBIT_URL) as conn:
    producer = conn.Producer()

    def process_msg(data, message):
        print('Received: {}'.format(data))

        action = actions.get(data.get('method'))

        if action:
            res = action(data)
            producer.publish(res, routing_key=message.properties['reply_to'],
                             correlation_id=message.properties.get('correlation_id'))
        else:
            print('Action handler not found!')

        # if body.get('resource') == 'user':
        #     users = db.session.query(User).filter(User.id.in_(body['ids']))
        #     data = [u.asdict() for u in users]
        #
        #     producer.publish(data, routing_key=message.properties['reply_to'],
        #                      correlation_id=message.properties.get('correlation_id'))

    with conn.Consumer(rpc_queue, callbacks=[process_msg]) as consumer:
        while True:
            conn.drain_events()
