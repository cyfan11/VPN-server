from http import client
import sys
import os
import time
import re
import socket
from threading import Thread

from select import select
import ssl
'''
Solution to HW4

Authors: Chris Feng and Cynthia Fan

'''


def forwarder(server_port, client_host, client_port, forwarder_type):
    '''
    Implementation of the forwarder
    @Parameters: 
        server_port: the port of the server inside the forwarder that the client is connecting to
        client_host: the IP address of outside destination
        client_port: the port of destination that the forwarder connect to
    '''

    try:
        #listening_socket
        fserver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fserver_socket.setblocking(False)
        fserver_socket.bind(("127.0.0.1", server_port))
        fserver_socket.listen(0)

        if (forwarder_type == 'D'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain('serv_certificate.pem', 'serv_privkey.pem')

            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            fserver_socket = context.wrap_socket(fserver_socket, server_side=True)

        elif (forwarder_type == 'E'):
            context = ssl.create_default_context()
            context.load_verify_locations('ca_certificate.pem')

            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
    
    except:
        print("Error preparing the server socket")
        sys.exit()

    client_sockets = []
    send_dic = {}
    pending_dic = {}

    while True:
        rlist = [fserver_socket] 
        wlist = []
        xlist = []

        #construct the reading list from client sockets
        for client_socket in client_sockets:
            rlist.append(client_socket)
        #construct the writing list from those sockets that have pending message
        for pending_socket in pending_dic.keys():
            rlist.remove(send_dic[pending_socket])
            wlist.append(pending_socket)


        rlist, wlist, xlist = select(rlist, wlist, xlist)

        #when the server inside is listening
        if fserver_socket in rlist:
                # connect socket to the inside server

                (connection_socket, address) = fserver_socket.accept()
                #connection_socket.setblocking(False)
                client_sockets.append(connection_socket)
                #find the corresponding destination socket
                
                destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #destination_socket.setblocking(False)
                

                #if E, turn destination_socket into TLS
                if (forwarder_type == 'E'):
                    destination_socket = context.wrap_socket(destination_socket) 
                destination_socket.connect((client_host, client_port))
                destination_socket.setblocking(False)
                client_sockets.append(destination_socket)

                #map the two sockets and the direction
                send_dic[connection_socket] = destination_socket
                send_dic[destination_socket] = connection_socket

        for r in client_sockets:
            #if the socket is reading, recv and send message 
            if r in rlist:
                s = send_dic[r]
                try:
                    data = r.recv(1024) 
                except ssl.SSLError as err:
                    print(err)
                    continue

                data_sent = s.send(data)
                # if the message is not completely flushed, map the socket and remaining message
                if len(data) == 0:
                    r.close()
                    s.close()
                if len(data) != data_sent:    
                    data_pending = data[data_sent:] 
                    pending_dic[s] == data_pending 

            #if the socket is writing, keep flushing until everything is sent 
            elif r in wlist:
                send_remaining = r.send(pending_dic[r])
                still_pending = data[send_remaining:]
                if len(still_pending) != 0:
                    pending_dic[r] = still_pending



forwarder(8080,"127.0.0.1",9000,'E')