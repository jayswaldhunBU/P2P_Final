from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
socketio = SocketIO(app)
db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))

    def __repr__(self):
        return '<Message %r>' % self.content


@app.route('/')
def index():
    messages = Message.query.all()
    return render_template('index.html', messages=messages)


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(msg):
    print('Received message:', msg)
    message = Message(content=msg)
    db.session.add(message)
    db.session.commit()
    emit('message', msg, broadcast=True)


def start_server():
    socketio.run(app, host='0.0.0.0', port=5000)


def start_client():
    import socket
    import time

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('localhost', 5000))
            print('Connected to server')
            break
        except:
            print('Server not available. Retrying in 5 seconds...')
            time.sleep(5)

    while True:
        try:
            msg = input('Enter message to send: ')
            s.sendall(msg.encode())
            print('Message sent')
        except:
            print('Server disconnected. Retrying in 5 seconds...')
            s.close()
            time.sleep(5)
            start_client()


if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    threading.Thread(target=start_client).start()
