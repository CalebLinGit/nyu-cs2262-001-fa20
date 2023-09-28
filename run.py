'''
Author: Caleb Lin
Date: 2023-09-28 00:56:20
LastEditors: Yicheng Lin
LastEditTime: 2023-09-28 01:39:24
Description: 
'''
from flask import Flask
import datetime as dt
import pytz

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/time')  
def current_time():  
    now = dt.datetime.now(pytz.timezone('US/Eastern'))  
    current_time = now.strftime("%H:%M:%S")  
    return "Current Time: {}".format(current_time)

app.run(host='0.0.0.0',
        port=8080,
        debug=True)
