# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 09:50:58 2022

@author: pc1
"""

import time
import sys
from functools import partial
import zmq
import signal

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
        
        string = sock_cluster_sub.recv_string()
        zipcode, pub_time, temperature, relative_humidity = string.split()
        total_temp = int(temperature)

        # If temperature is greater than 130, stream back to the weather station (data Rec) for concern
        if total_temp > 130:
            rec_2.append([pub_time, time.time_ns(), zip_filter, run, relative_humidity])
            print(f"From Data Received: {zipcode} {pub_time} {temperature}")
            sock_gui_pub.send_string(f"{zipcode} {pub_time} {temperature} {relative_humidity}")
            print(f"Counted packets {count}")
            count += 1
        
        # time.sleep(0.0001)

    run = not run
    print("Cluster Module Stopped")

app = QApplication([])
window = QWidget()
window.resize(300, 300)
window.setWindowTitle("Cluster Module")
layout = QVBoxLayout()

button = QPushButton("Cluster")
button.clicked.connect(partial(greet, "World!"))
layout.addWidget(button)
message = QLabel("")
layout.addWidget(message)
window.setLayout(layout)


ctx = zmq.Context()

# Collecting updates from weather server...
sock_cluster_sub = ctx.socket(zmq.SUB)
print("Collecting updates from weather server...")
sock_cluster_sub.connect("tcp://localhost:5557")

# Subscribe to data_rec, default is Cluster, 10003
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "1001"
sock_cluster_sub.setsockopt_string(zmq.SUBSCRIBE, zip_filter)

# Be publisher if temperature is greater than 130
sock_gui_pub = ctx.socket(zmq.PUB)
sock_gui_pub.bind("tcp://*:5570")

rec_2 = []


window.show()    
app.exec()























