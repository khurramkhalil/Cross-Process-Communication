# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 09:50:58 2022

@author: pc1
"""

import sys
import time
import zmq
import signal
from functools import partial

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

run = True

def signal_handler(signal, frame):
    global run
    print("Stopping")
    run = not run

signal.signal(signal.SIGINT, signal_handler)
def greet(name):
    global run
    count = 1
    while run:
        
        string = sock_tewa_sub.recv_string()
        zipcode, pub_time, temperature, relative_humidity = string.split()
        # total_temp = int(temperature)

        # From Cluster
        try:
            string = sock_cluster_sub.recv_string(flags=zmq.NOBLOCK)
            zip_filter, pub_time, CLUSTER, relative_humidity = string.split()
            rec_2.append([pub_time, time.time_ns(), zip_filter, CLUSTER, relative_humidity])
            # print(f"Cluster Feedback: {pub_time} {time.time_ns()} {zip_filter}")
            
            rec_1.append([pub_time, time.time_ns(), zip_filter, temperature, relative_humidity])
            # print(f"From Data Received: {zipcode} {pub_time} {temperature}")
            sock_gui_pub.send_string(f"{zipcode} {pub_time} {temperature} {relative_humidity}")
            print(f"Counted packets {count}")
            count += 1
                
        except zmq.Again:
            pass
    
    run = not run
    print("TEWA Module Stopped")

app = QApplication([])
window = QWidget()
window.resize(300, 300)
window.setWindowTitle("TEWA Module")
layout = QVBoxLayout()

button = QPushButton("TEWA")
button.clicked.connect(partial(greet, "World!"))
layout.addWidget(button)
message = QLabel("")
layout.addWidget(message)
window.setLayout(layout)


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

rec_1 = []
rec_2 = []


window.show()    
sys.exit(app.exec())







