'''
Author: Caleb Lin
Date: 2023-09-28 00:56:20
LastEditors: Yicheng Lin
LastEditTime: 2023-10-12 16:17:08
Description: 
'''

import socket
import pickle
import os
import re
# app = Flask(__name__)

path = "dns_records.pickle"
dns_dict = dict()
dns_parameter_list = ["TYPE","NAME","VALUE","TTL"]

# adapt from https://code.activestate.com/recipes/491264-mini-fake-dns-server/
def mini_udp_service(message, client_address, server_socket):   
    
    fields = dict()

    # extract fields using regex
    lines = message.decode().split("\n")
    fields = {line.split('=')[0].strip(): line.split('=')[1].strip() for line in lines if '=' in line}
    
    # register
    if "VALUE" in fields.keys():  
        if not all(key in fields for key in ["TYPE", "NAME", "VALUE", "TTL"]):
            server_socket.sendto('Missing parameters for registration'.encode(), client_address)
            return
        hostname = fields["NAME"]
        ip_address = fields["VALUE"]
        dns_dict[hostname] = ip_address
        # Save to a file for persistence
        pickle.dump(dns_dict, open(path, "wb"))
        server_socket.sendto('Registration successful'.encode(), client_address)

    # DNS Query
    else:  
        if not all(key in fields for key in ["TYPE", "NAME"]):
            server_socket.sendto('Missing parameters for query'.encode(), client_address)
            return
        hostname = fields["NAME"]
        if hostname in dns_dict:
            ip_address = dns_dict[hostname]
            response = "TYPE=A\nNAME={}\nVALUE={}\nTTL=10".format(hostname, ip_address)
            server_socket.sendto(response.encode(), client_address)
        else:
            server_socket.sendto('Record not found'.encode(), client_address)

if __name__ == "__main__":
    # persist
    try:
        dns_dict = pickle.load(open(path, "rb"))
    except (OSError, IOError) as e:
        pickle.dump(dns_dict, open(path, "wb"))
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 53533))

    print("Authoritative Server is ready to receive...")

    while True:
        message, client_address = server_socket.recvfrom(2048)
        mini_udp_service(message, client_address, server_socket)



