import RPi.GPIO as GPIO
from time import sleep

import os
import sys
import glob
import bluetooth
import re

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

print(f"Waiting for connection on RFCOMM channel {port}...\r")

recv_sock, client_info = server_sock.accept()

print(f"Connected to {client_info[0]}.\r")

read = "0"
message = ""

while read != "1000":
    read = recv_sock.recv(1024)
    read = read.decode("utf-8").strip('\n')
    print(f"{read}\r")

    message = ""

    # print(f"Sending: 'Acknowledge: {read}'")
    # Acknowledge ÖS command
    recv_sock.send(f"{read}, ".encode()) # Remember NEW LINE for ÖS to be able to read lines.
    # message = message + read

    # Send DWM data
    with open("position.txt", "r") as f:
        for line in f:
            line = line.strip("\n")
            x, y, z, qf = line.split()
            x = x.translate({ord(c): None for c in 'x:'})
            y = y.translate({ord(c): None for c in 'y:'})
            recv_sock.send(f"{x}, {y}, ".encode())
            # message = message + f"{x}, {y}, "
        f.close()

    # Send angle data
    recv_sock.send("0, ".encode())
    # message = message + "0, "

    # Send LIDAR data
    distances = []
    for i in range(360):
        distances.append(0)

    with open("distances.txt", "r") as f:
        for line in f:
            a, d = line.split()
            distances[int(a)] = int(d)
        f.close()

    for i in range(359):
        # print(f"({i}, {distances[i]})")
        recv_sock.send(f"{distances[i]}, ".encode())
        # message = message + f"{distances[i]}, "
    recv_sock.send(f"{distances[i]}\n".encode())
    # message = message + f"{distances[360]}\n"
    # recv_sock.send(message.encode())


    # Send LIDAR data
    # if read == "77":
    #     # Remove for KTS
    #     recv_sock.send("EOD\n".encode())

    # Send DWM data
    # if read == "88":

print("Shutting down...")
server_sock.close()
