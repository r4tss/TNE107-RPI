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

    if read == "11" or read == "22":
        sleep(0.5)
    else:
        sleep(1)

    print("0\r")

    # print(f"Sending: 'Acknowledge: {read}'")
    # Acknowledge ÖS command
    recv_sock.send(f"{read}, ".encode()) # Remember NEW LINE for ÖS to be able to read lines.
    # message = message + read

    # Send DWM data
    with open("position.txt", "r") as f:
        for line in f:
            line = line.strip("\n")
            x, y, z, qf = line.split(",")
            x = int(float(x) * 1000)
            y = int(float(y) * 1000)
            print(f"x: {x}, y: {y}")
            recv_sock.send(f"{x}, {y}, ".encode())
            # message = message + f"{x}, {y}, "
        f.close()

    # Send angle data
    with open("angle.txt", "r") as f:
        for line in f:
            angle = line.strip("\n")
            print(angle)
            recv_sock.send(f"{angle}, ".encode())

    recv_sock.send("0, ".encode()) # Near goal
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

print("Shutting down...")
server_sock.close()
