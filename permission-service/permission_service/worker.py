import os
from kombu import Connection, Queue

RABBIT_URL = os.environ.get('RABBIT_URL', 'amqp://192.168.99.101:5672')

rpc_queue = Queue(name='permission_rpc', durable=False, no_ack=True)


def check_permission(data):
    print('check_permission called!', data)
    return dict(should_continue=True)

actions = {
    'check': check_permission
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

    # def process_msg(body, message):
    #     print('Received: {}'.format(body))
    #     if body.get('event') == 'newsletter:beforeFetch':
    #         data = dict(allowed=True)
    #
    #         producer.publish(data, routing_key=message.properties['reply_to'],
    #                          correlation_id=message.properties.get('correlation_id'))
    #
    # with conn.Consumer(rpc_queue, callbacks=[process_msg]) as consumer:
    #     while True:
    #         conn.drain_events()
