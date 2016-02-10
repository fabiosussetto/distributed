import os
from kombu import Connection, Queue, Exchange, common

RABBIT_URL = os.environ['RABBIT_URL']

events_exchange = Exchange('broadcast', type='fanout', durable=True)
events_queue = Queue(name=common.uuid(), exchange=events_exchange)


def process_msg(body, message):
    print('Received: {}'.format(body))
    message.ack()


with Connection(RABBIT_URL) as conn:
    with conn.Consumer(events_queue, callbacks=[process_msg]) as consumer:
        while True:
            conn.drain_events()
