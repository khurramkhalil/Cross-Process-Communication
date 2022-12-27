# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 09:50:58 2022

@author: pc1
"""

import time
import zmq
import sys

ctx = zmq.Context()

# Collecting updates from weather server...
sock_tewa_sub = ctx.socket(zmq.SUB)
print("Collecting updates from weather server...")
sock_tewa_sub.connect("tcp://localhost:5557")

# Subscribe to data_rec, default is TEWA, 10002
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10002"
sock_tewa_sub.setsockopt_string(zmq.SUBSCRIBE, zip_filter)

# Be publisher if temprature is greater than 120
sock_gui_pub = ctx.socket(zmq.PUB)
sock_gui_pub.bind("tcp://*:5560")

# Getting Feedback from client 'Cluster' if temprature is high
sock_cluster_sub = ctx.socket(zmq.SUB)
sock_cluster_sub.connect("tcp://localhost:5570")
sock_cluster_sub.setsockopt_string(zmq.SUBSCRIBE, '')

# Process 500 updates
rec_1 = []
rec_2 = []
for update_nbr in range(100):
    string = sock_tewa_sub.recv_string()
    zipcode, pub_time, temperature, relhumidity = string.split()
    total_temp = int(temperature)
    
    # If temprature is greater than 120, stream back to the weather station (data Rec) for concern
    if int(temperature) > 125:
        rec_1.append([pub_time, time.time_ns(), zip_filter, temperature, relhumidity])
        print(f"From Data Recieved: {zipcode} {pub_time} {temperature}")
        sock_gui_pub.send_string(f"{zipcode} {pub_time} {temperature} {relhumidity}")

    # From Cluster
    try:
        string = sock_cluster_sub.recv_string(flags=zmq.NOBLOCK)
        zip_filter, pub_time, temp, relhumidity = string.split()
        rec_2.append([pub_time, time.time_ns(), zip_filter, temp, relhumidity])
        print(f"Cluster Feedback: {pub_time} {time.time_ns()} {zip_filter}")

    except zmq.Again:
        pass




