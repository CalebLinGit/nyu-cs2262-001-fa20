'''
Author: Caleb Lin
Date: 2023-09-28 00:56:20
LastEditors: Yicheng Lin
LastEditTime: 2023-10-12 16:33:57
Description: 
'''
from flask import Flask, request, jsonify
import socket
import re

app = Flask(__name__)

parameter_list = ["hostname","ip","as_ip","as_port"]
parameter_dict = dict()

def calculate_fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

@app.route('/')
def hello_world():
    return 'Hello world!'

# register to AS
@app.route('/register', methods=['PUT'])
def register():    
    
    # extract params from post data 
    for parameter in parameter_list:
        parameter_dict[parameter] = request.json.get(parameter)
    
    print(parameter_dict)
    # Construct the DNS registration message
    message = "TYPE=A\nNAME={}\nVALUE={}\nTTL=10".format(parameter_dict["hostname"], parameter_dict["ip"])

    # Send the registration message to the Authoritative Server via UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(message.encode(), (parameter_dict["as_ip"], int(parameter_dict["as_port"])))
        response, server_address = s.recvfrom(2048)
    if b'successful' in response:
        return jsonify({"message": "Registration successful"}), 201
    else:
        return jsonify({"error": "Registration failed"}), 400

@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    number = request.args.get('number')
    try:
        x = int(number)
        if x <= 0:
            raise ValueError
        return jsonify({"fibonacci": calculate_fibonacci(x)}), 200
    except ValueError:
        return jsonify({"error": "Invalid number, need to provide sequence number >= 1!"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0',
            port=9090,
            debug=True)