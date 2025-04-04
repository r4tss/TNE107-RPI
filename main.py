import RPi.GPIO as GPIO
from time import sleep

import os
import glob
import bluetooth

import re

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.output(17, False)
GPIO.output(27, False)

target = "D4:D2:52:ED:14:89"

server_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

print("Waiting for connection on RFCOMM channel %d..." % port)

client_sock, client_info = server_sock.accept()

while client_sock:
    read = client_sock.recv(1024)
    read = read.decode("utf-8").strip('\n')
    print(read)

    if read == "11":
        GPIO.output(17, True)
        GPIO.output(27, False)
    elif read == "22":
        GPIO.output(17, False)
        GPIO.output(27, True)
    else:
        GPIO.output(17, False)
        GPIO.output(27, False)
pi@pigroup3:~/TNE107-RPI$ cat main.py 
import RPi.GPIO as GPIO
from time import sleep

import os
import glob
import bluetooth

import re

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.output(17, False)
GPIO.output(27, False)

target = "D4:D2:52:ED:14:89"

server_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

print("Waiting for connection on RFCOMM channel %d..." % port)

client_sock, client_info = server_sock.accept()

while client_sock:
    read = client_sock.recv(1024)
    read = read.decode("utf-8").strip('\n')
    print(read)

    if read == "11":
        GPIO.output(17, True)
        GPIO.output(27, False)
    elif read == "22":
        GPIO.output(17, False)
        GPIO.output(27, True)
    else:
        GPIO.output(17, False)
        GPIO.output(27, False)

GPIO.output(17, False)
GPIO.output(27, False)

print("Shutting down...")
server_sock.close()
print("Done.")
