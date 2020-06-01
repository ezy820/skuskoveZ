from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect    
import time
import math
import random
import serial

ser = serial.Serial('/dev/ttyS1',9600)
ser.baurate = 9600

async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


def background_thread(args):
    count = 0
    i = 0
    while True:
        if args:
          A = dict(args).get('A')
        else:
          A = 0
        A = int(A)
        ser.write(str(int(9)))
        kom = ser.readline()
        ser.write(str(A))
        data = kom.split(':')
        cas = time.time()
        socketio.sleep(0.5)
        if A != 0:
            count += 1
            print(data)
            socketio.emit('my_response',{'data': data[0], 'data2': data[1], 'count': count, 'time':cas}, namespace='/test')
        else:
            print(cas)
  
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count'], 'ampl':1})

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@app.route('/')
def index():
    return render_template('tabs.html', async_mode=socketio.async_mode)

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()
    
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)
