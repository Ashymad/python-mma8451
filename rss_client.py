#!/usr/bin/env python
# -*- coding:utf-8, indent=tab, tabstop=4 -*-
#
# See 'LICENSE'  for copying
#
# This file contains the code for the client module of 'accel.py'
#
# Revision history
# Date          Author                  Version     Details
# ----------------------------------------------------------------------------------
# 2018-01-18    Massimo Di Primio       0.06        1st file implementation

"""Client thread worker - This is a simple client code example for 'accel'.py' program"""

import logging
import time
import socket
import datetime
import json
import rss_client_messages as climsg


def cli_connect(params):
    """Open connection to the server"""
    server_address = (str(params['serveraddress']), int(params['servertcpport']))
    logging.debug('Trying to connect to server ' + str(server_address))
    # Create a TCP/IP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect the socket to the port where the server is listening
        s.connect(server_address)
        logging.debug('Connection Established to server ' + str(server_address))
    except:
        logging.debug(
            "Failed to open connection: " + str(params['serverprotocol']) +
            ", to IP: " + str(params['serveraddress']) + 
            ", on port: " + str(params['servertcpport'])
            )
        return(-1)

    return(s)


def cli_close(s):
    """Close the server connection"""
    if s > -1:
        s.close()


def cli_worker(stopEvent, config, accelBuffer):
    """A client worker as thread"""
    logging.debug('Thread Starting')
    s = cli_connect(config)
    send_client_hello(s)

    ts = int(time.time())
    te = ts
    while not stopEvent.wait(0.3):
        if len(accelBuffer) > 0:
            send_accel_data(s, accelBuffer)
            te = int(time.time())
        if (te - ts) > 10:
            send_client_heartbit(s)
            ts = int(time.time())

        time.sleep(0.5)
    send_zap_message(s)
    cli_close(s)
    logging.debug("Thread cliWorker is terminating as per your request.")

    
def send_accel_data(s, accelBuffer):
    """Send acceleration data to the server"""
    pbuf = parse_accel_data(accelBuffer)
    # if len(pbuf) > 0: # this sometimes returns error (when buf is empty, it has None type)
    if (pbuf is not None) and (len(pbuf) > 0):
        str = climsg.accel_data_message(pbuf)
        try:
            s.sendall(json.dumps(str) + "\n")
        except:
            logging.debug("Failed to send Acceleration-Data to the server")


def send_client_hello(s):
    """Send Hello message to the server"""
    try:
        s.sendall(json.dumps(climsg.hello_message()) + "\n")
    except:
        logging.debug("Failed to send Hello to the server")


def send_zap_message(s):
    """Send Zap message to the server"""
    try:
        s.sendall(json.dumps(climsg.zap_message()) + "\n")
    except:
        logging.debug("Failed to send Zap to the server")


def send_config_affirm_message(s, config):
    """Send client configuration to server"""
    try:
        s.sendall(json.dumps(climsg.config_affirm_message(config)) + "\n")
    except:
        logging.debug("Failed to send client configuration to the server")


def send_client_heartbit(s):
    """Send Heartbit to the server"""
    try:
        s.sendall(json.dumps(climsg.heart_bit()) + "\n")
    except:
        logging.debug("Failed to send heartbit to the server")


def parse_accel_data(b):
    """Parse acceleration data to make sure we only send meaningfull data to the server"""
    tsh = 10
    tbuf = []
    # tbuf.append([0, 0, 0, 0, 0])
    # bLength = len(b)
    # logging.debug("parseAccelData(b) # of elements   = " + str(len(b)))
    if len(b) > 1:
        logging.debug("parseAccelData: In  AccelData/BufLen: " + str(len(b)) + "/" +str(len(tbuf)))
        firstTime = 1
        prow = None
        for row in b:
            crow = b.pop(0)     # Get the oldest record
            if firstTime == 1:
                prow = crow
                firstTime = 0
            if ( (abs(abs(int(crow[1])) - abs(int(prow[1]))) > tsh) or
                 (abs(abs(int(crow[2])) - abs(int(prow[2]))) > tsh) or
                 (abs(abs(int(crow[3])) - abs(int(prow[3]))) > tsh)
                ):
                tbuf.append(crow)
                prow = crow
                print ("Again PROW/CROW/TBUFLEN:" + str(prow) + " / " + str(crow) + " / " +  str(len(tbuf)))
        
        logging.debug("parseAccelData: Out AccelData/BufLen: " + str(len(b)) + "/" +str(len(tbuf)))
        return(tbuf)

