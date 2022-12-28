# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 09:50:58 2022

@author: pc1
"""

import sys
import time

import zmq

ctx = zmq.Context()

# Collecting updates from weather server...
sock_tewa_sub = ctx.socket(zmq.SUB)
print("Collecting updates from weather server...")
sock_tewa_sub.connect("tcp://localhost:5557")

# Subscribe to data_rec, default is TEWA, 10002
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10002"
sock_tewa_sub.setsockopt_string(zmq.SUBSCRIBE, zip_filter)

# Be publisher if temperature is greater than 120
sock_gui_pub = ctx.socket(zmq.PUB)
sock_gui_pub.bind("tcp://*:5560")

# Getting Feedback from client 'Cluster' if temperature is high
sock_cluster_sub = ctx.socket(zmq.SUB)
sock_cluster_sub.connect("tcp://localhost:5570")
sock_cluster_sub.setsockopt_string(zmq.SUBSCRIBE, '')

# Process 500 updates
rec_1 = []
rec_2 = []
for update_nbr in range(100):
    string = sock_tewa_sub.recv_string()
    zipcode, pub_time, temperature, relative_humidity = string.split()
    total_temp = int(temperature)

    # From Cluster
    try:
        string = sock_cluster_sub.recv_string(flags=zmq.NOBLOCK)
        zip_filter, pub_time, temp, relative_humidity = string.split()
        rec_2.append([pub_time, time.time_ns(), zip_filter, temp, relative_humidity])
        print(f"Cluster Feedback: {pub_time} {time.time_ns()} {zip_filter}")

    except zmq.Again:
        pass

    # If temperature is greater than 125, stream back to the GUI State for registering
    if int(temperature) > 125:
        rec_1.append([pub_time, time.time_ns(), zip_filter, temperature, relative_humidity])
        print(f"From Data Received: {zipcode} {pub_time} {temperature}")
        sock_gui_pub.send_string(f"{zipcode} {pub_time} {temperature} {relative_humidity}")
