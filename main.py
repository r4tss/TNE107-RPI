import RPi.GPIO as GPIO
from time import sleep

import os
import sys
import glob
import bluetooth
import re

# 3 Pins to communicate with Arduino
P1 = 17
P2 = 27
P3 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(P1, GPIO.OUT)
GPIO.setup(P2, GPIO.OUT)
GPIO.setup(P3, GPIO.OUT)
GPIO.output(P1, False)
GPIO.output(P2, False)
GPIO.output(P3, False)

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

print("Waiting for connection on RFCOMM channel %d..." % port)

client_sock, client_info = server_sock.accept()

print("Connected to %s." % client_info[0])

while client_sock:
    read = client_sock.recv(1024)
    read = read.decode("utf-8").strip('\n')
    print("Received: %s" % read)

    sock.send("Acknowledge: " + read)
    print("Sent acknowledge")

    if read == "0":      # Do nothing
        GPIO.output(P1, False)
        GPIO.output(P2, False)
        GPIO.output(P3, False)
    elif read == "11":   # Drive forward
        GPIO.output(P1, True)
        GPIO.output(P2, False)
        GPIO.output(P3, False)
    elif read == "22": # Drive backward
        GPIO.output(P1, False)
        GPIO.output(P2, True)
        GPIO.output(P3, False)
    elif read == "33": # Rotate right, 90 degrees
        GPIO.output(P1, True)
        GPIO.output(P2, True)
        GPIO.output(P3, False)
    elif read == "44": # Rotate left, 90 degrees
        GPIO.output(P1, False)
        GPIO.output(P2, False)
        GPIO.output(P3, True)
    elif read == "55": # Rotate right, 45 degrees
        GPIO.output(P1, True)
        GPIO.output(P2, False)
        GPIO.output(P3, True)
    elif read == "66": # Rotate left, 45 degrees
        GPIO.output(P1, False)
        GPIO.output(P2, True)
        GPIO.output(P3, True)
    elif read == "98": # Turn on light at landmark
        GPIO.output(P1, True)
        GPIO.output(P2, True)
        GPIO.output(P3, True)
    else:              # Do nothing if command is not recognized
        GPIO.output(P1, False)
        GPIO.output(P2, False)
        GPIO.output(P3, False)

GPIO.output(P1, False)
GPIO.output(P2, False)
GPIO.output(P3, False)

print("Shutting down...")
server_sock.close()
