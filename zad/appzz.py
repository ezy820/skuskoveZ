from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import time
import random
import math
import serial

async_mode = None

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 
ser=serial.Serial("/dev/ttyS1",9600)
ser.baudrate=9600

def background_thread(args):
    count = 0    
    i = 0
    dataList = []
    while True:
        ser.write(str(int(9)))
        socketio.sleep(0.5)
        
        count += 1
       
        #btnV = dict(args).get('btn_value')
        if dict(args).get('A') is not None:
            A = dict(args).get('A')
            A = int(A)
            print A
        
          #sliderV = dict(args).get('slider_value')
        if A>0:
            
            if i==0 or i!=A:
          #btnV = 'null'
          #print A
          #sliderV = 0
                ser.write(str(A))
                i=A
                print i
            t=time.time()
            read_ser=ser.readline()
            prem=read_ser.split(',')
          #print(read_ser)
            dataDict = {
          "t": time.time(),
          "x": count,
          "y": prem[0],
          "y2": prem[1]}
            dataList.append(dataDict)
        
            if len(dataList)>0:
            
            #print str(dataList)
                print(count)
                print(prem[0])
                print(prem[1])
                print(A)
                
            
                socketio.emit('my_response',
                    {'data': prem[0], 'data2': prem[1], 'count': count, 'time': t},
                      namespace='/test')

@app.route('/')
def index():
    return render_template('index1.html', async_mode=socketio.async_mode)
      
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['receive_count'] = session.get('receive_count', 0) + 1 
    session['A'] = message['value']    
    emit('my_response',
         {'data': message['value'], 'count': session['receive_count'], 'ampl':1})
 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('click_event', namespace='/test')
def db_message(message):   
    session['btn_value'] = message['value']    

@socketio.on('slider_event', namespace='/test')
def slider_message(message):  
    #print message['value']   
    session['slider_value'] = message['value']  

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)