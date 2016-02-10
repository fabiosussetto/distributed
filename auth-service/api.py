import os

from flask import Flask, g, request
from flask.ext.json import FlaskJSON, as_json
from kombu import Connection, Exchange, Queue

app = Flask(__name__)
json = FlaskJSON(app)

RABBIT_URL = os.environ['RABBIT_URL']

broadcast_exchange = Exchange('broadcast', type='fanout', durable=True)
events_queue = Queue('events', exchange=broadcast_exchange)


def _get_rabbit_conn():
    rabbit_conn = getattr(g, '_rabbit_conn', None)
    if rabbit_conn is None:
        rabbit_conn = g._rabbit_conn = Connection(RABBIT_URL)
    return rabbit_conn


@app.teardown_appcontext
def close_connection(exception):
    rabbit_conn = getattr(g, '_rabbit_conn', None)
    if rabbit_conn is not None:
        rabbit_conn.release()


def broadcast_message(body):
    conn = _get_rabbit_conn()
    producer = conn.Producer(serializer='json')
    producer.publish(body, exchange=broadcast_exchange, routing_key='events', declare=[events_queue])


@app.route('/signup', methods=['POST'])
@as_json
def signup_handler():
    data = request.get_json()
    broadcast_message(dict(type='signup:new', data=data))
    return dict(ok=True)


if __name__ == '__main__':
    app.run(debug=True)
