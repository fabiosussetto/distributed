import os

from dictalchemy.utils import make_class_dictable
from flask import Flask, g, request
from flask.ext.json import FlaskJSON, as_json
from flask_sqlalchemy import SQLAlchemy
from kombu import Connection, Exchange, Queue

RABBIT_URL = os.environ.get('RABBIT_URL', 'amqp://192.168.99.101:5672//')
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',
                                         'postgresql://postgres:@192.168.99.101:5432/auth_service')


app = Flask(__name__)
json = FlaskJSON(app)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


broadcast_exchange = Exchange('broadcast', type='fanout', durable=True)
events_queue = Queue('events', exchange=broadcast_exchange)

make_class_dictable(db.Model)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username


def _get_rabbit_conn():
    rabbit_conn = getattr(g, '_rabbit_conn', None)
    if rabbit_conn is None:
        rabbit_conn = g._rabbit_conn = Connection(RABBIT_URL)
    return rabbit_conn


db.create_all()


@app.teardown_appcontext
def close_connection(exception):
    rabbit_conn = getattr(g, '_rabbit_conn', None)
    if rabbit_conn is not None:
        rabbit_conn.release()


def broadcast_message(body):
    conn = _get_rabbit_conn()
    producer = conn.Producer()
    producer.publish(body, exchange=broadcast_exchange, routing_key='events', declare=[events_queue])


@app.route('/signup', methods=['POST'])
@as_json
def signup_handler():
    data = request.get_json()
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()

    broadcast_message(dict(type='auth:user:created', data=dict(user=user.asdict())))
    return dict(ok=True)


@app.route('/update', methods=['PUT'])
@as_json
def edit_user_handler():
    data = request.get_json()
    user = User.query.get(1)

    broadcast_message(dict(type='auth:user:changed', data={'username': 'test'}))
    db.session.commit()
    return dict(ok=True)


if __name__ == '__main__':
    app.run(debug=True)
