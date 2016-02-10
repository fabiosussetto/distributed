import os
from kombu import Connection, Exchange, Queue

RABBIT_URL = os.environ['RABBIT_URL']

broadcast_exchange = Exchange('broadcast', type='fanout', durable=True)
events_queue = Queue('events', exchange=broadcast_exchange)

with Connection(RABBIT_URL) as conn:
    producer = conn.Producer(serializer='json')
    producer.publish({'foo': 'bar'}, exchange=broadcast_exchange, routing_key='events', declare=[events_queue])
