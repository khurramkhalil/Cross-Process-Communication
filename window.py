import sys
from functools import partial
import time
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
    # if message.text():
    #     message.setText("")
    #     print("Clustering Module will be Starting on Next Click")

    # else:
    # message.setText(f"Cluster Module Stopped, {name}")
    while run:
        time.sleep(0.19)
        print("Transmitting clusters")
    run = not run
    print("Cluster Module Stopped")


app = QApplication([])
window = QWidget()
window.resize(300, 300)
window.setWindowTitle("Cluster Module")
layout = QVBoxLayout()

button = QPushButton("CLUSTER")
button.clicked.connect(partial(greet, "World!"))
layout.addWidget(button)
message = QLabel("")
layout.addWidget(message)
window.setLayout(layout)
window.show()
app.exec()
# sys.exit(app.exec())
