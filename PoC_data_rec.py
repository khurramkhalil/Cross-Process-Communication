# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 09:43:02 2022

@author: pc1
"""

import time
from random import randrange

import zmq

ctx = zmq.Context()

# Streaming temperature of the all states
sock_data_pub = ctx.socket(zmq.PUB)
sock_data_pub.bind("tcp://*:5557")

# Getting Feedback from client 'GUI state' if temperature is high
sock_data_sub = ctx.socket(zmq.SUB)
sock_data_sub.connect("tcp://localhost:5550")
sock_data_sub.setsockopt_string(zmq.SUBSCRIBE, '')

time_ = []
rec_ = []
time_1 = []
time_2 = []
record = 0
while True:
    if record == 0:
        time.sleep(9)
    time.sleep(0.001)
    zipcode = randrange(1000, 1015)
    temperature = randrange(100, 135)
    relative_humidity = str(randrange(10, 60)) # * 100000  # randrange(10, 60)
    time_record = time.time_ns()

    if zipcode == 10001 and temperature > 120:
        time_.append([f"{zipcode} {time_record} {temperature} {relative_humidity}"])
        print("Condition met, expect a reply from GUI")

    elif zipcode == 10002 and temperature > 125:
        time_1.append([f"{zipcode} {time_record} {temperature} {relative_humidity}"])
        print("Condition met, expect an increment in TEWA")

    elif zipcode == 10003 and temperature > 130:
        time_2.append([f"{zipcode} {time_record} {temperature} {relative_humidity}"])
        print("Condition met, expect an increment in Cluster")

    sock_data_pub.send_string(f"{zipcode} {time_record} {temperature} {relative_humidity}")

    # From GUI
    try:
        string = sock_data_sub.recv_string(flags=zmq.NOBLOCK)
        zip_filter, pub_time, temp, relative_humidity = string.split()
        rec_.append([pub_time, time.time_ns(), zip_filter, temp, relative_humidity])

    except zmq.Again:
        pass

    record += 1
    if record == 20000:
        break

# rr = rec_[0]
# float(rr[1]) - float(rr[0])
