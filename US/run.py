'''
Author: Caleb Lin
Date: 2023-09-28 00:56:20
LastEditors: Yicheng Lin
LastEditTime: 2023-10-12 16:26:02
Description: 
'''
from flask import Flask, request,Response, jsonify
import socket
import requests

app = Flask(__name__)

parameter_list = ["hostname","fs_port","seq_number","as_ip","as_port"]
parameter_dict = dict()

@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/fibonacci', methods=["GET"])
def fib():
    # get params
    for parameter in parameter_list:
        parameter_dict[parameter] = request.args.get(parameter,"Warning: Missing Parameter")
    
    # check and abort when meeting miss params
    if "Warning: Missing Parameter" in parameter_dict.values:
        return jsonify({"error": "Missing Parameters!"}), 400

    # make DNS query to the AS to get the IP address of the FS
    dns_query = "TYPE=A\nNAME={}".format(parameter_dict["hostname"])
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(dns_query.encode(), (parameter_dict["as_ip"], int(parameter_dict["as_port"])))
        response, _ = s.recvfrom(2048)

    # extract IP address from the DNS response using regex to address all the cases 
    lines = response.decode().split("\n")
    fields = {line.split('=')[0].strip(): line.split('=')[1].strip() for line in lines if '=' in line}
    if not all(key in fields for key in ["TYPE", "NAME", "VALUE"]):
        return jsonify({"error": "Failed to resolve hostname"}), 500
    parameter_dict["fs_ip"] = fields['VALUE']

    # response
    try:
        query_url = "http://{}:{}/fibonacci?number={}".\
            format(parameter_dict["fs_ip"],parameter_dict["fs_port"], parameter_dict["seq_number"])
        response = requests.get(query_url)
        response.raise_for_status()
        return response.json(), 200
    except requests.RequestException:
        return jsonify({"error": "Error from FS!"}), 400

    
if __name__ == "__main__":
    app.run(host='0.0.0.0',
            port=8080,
            debug=True)
