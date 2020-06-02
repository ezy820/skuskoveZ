from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect  
import time
import random
import math
import serial
import ConfigParser
import MySQLdb

async_mode = None

app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('config.cfg')
myhost = config.get('mysqlDB', 'host')
myuser = config.get('mysqlDB', 'user')
mypasswd = config.get('mysqlDB', 'passwd')
mydb = config.get('mysqlDB', 'db')
print myhost

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 
ser=serial.Serial("/dev/ttyS1",9600)
ser.baudrate=9600

def background_thread(args):
    count = 0    
    i = 0
    dataCounter =0
    dataList = []
    while True:
        ser.write(str(int(9)))
        socketio.sleep(0.5)
        count += 1
        dataCounter +=1
        if dict(args).get('A') is not None:
            A = dict(args).get('A')
            A = int(A)
            #print A
            dbV = dict(args).get('db_value')
          #sliderV = dict(args).get('slider_value')
        if A>0:
            
            if i==0 or i!=A:
                ser.write(str(A))
                i=A
                #print i
            t=time.time()
            read_ser=ser.readline()
            prem=read_ser.split(',')
            dataDict = {
          "t": time.time(),
          "x": count,
          "y": prem[0],
          "y2": prem[1]}
            dataList.append(dataDict)
        
            if len(dataList)>0:
                #print str(dataList)
                #print(count)
                #print(prem[0])
                #print(prem[1])
                #print(A)
                #print(dbV)
                socketio.emit('my_response',
                    {'data': prem[0], 'data2': prem[1], 'count': count, 'time': t},
                      namespace='/test')

@app.route('/')
def index():
    return render_template('index1.html', async_mode=socketio.async_mode)
      
@app.route('/graph', methods=['GET', 'POST'])
def graph():
    return render_template('graph.html', async_mode=socketio.async_mode)
    
@app.route('/db', methods=['GET', 'POST'])
def db():
    db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
    print request.form["data"]
    fuj = str(request.form["data"])
    cursor = db.cursor()
    cursor.execute("INSERT INTO zadanie (hodnoty) VALUES (%s)", [fuj])
    db.commit()
    fo = open("static/test.txt","a+")
    fo.write("%s\r\n" %fuj)
    db.close()
    return jsonify("ok")

@app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
def dbdata(num):
  db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
  cursor = db.cursor()
  print num
  cursor.execute("SELECT hodnoty FROM zadanie WHERE id=%s", num)
  rv = cursor.fetchone()
  return str(rv[0])


@app.route('/read/<string:num>', methods=['GET', 'POST'])
def readmyfile(num):
    fo = open("static/test.txt","r")
    rows = fo.readlines()
    return rows[int(num)-1]

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