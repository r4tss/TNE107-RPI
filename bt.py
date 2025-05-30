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
    print(f"{read}")

    if "98" in read:
        while read == "98":
            read = sys.stdin.readline().strip('\n')
            print(f"{read}")
            with open("position.txt", "r") as f:
                for line in f:
                    line = line.strip("\n")
                    x, y = line.split(",")
                    x = int(x)
                    y = int(y)
                    recv_sock.send(f"98, {x}, {y}\n".encode())
                    # message = message + f"{x}, {y}, "
                f.close()
        read = "99"
    else:
        sleep(0.5)

    # Acknowledge ÖS command
    recv_sock.send(f"{read}, ".encode()) # Remember NEW LINE for ÖS to be able to read lines.

    # Send DWM data
    if read == "10":
        sleep(1)
        with open("position_mean.txt", "r") as f:
            for line in f:
                line = line.strip("\n")
                x, y = line.split(",")
                x = int(x)
                y = int(y)
                recv_sock.send(f"{x}, {y}, ".encode())
                # message = message + f"{x}, {y}, "
            f.close()
    else:
        with open("position.txt", "r") as f:
            for line in f:
                line = line.strip("\n")
                x, y = line.split(",")
                x = int(x)
                y = int(y)
                recv_sock.send(f"{x}, {y}, ".encode())
                # message = message + f"{x}, {y}, "
            f.close()

    # Send angle data
    with open("angle.txt", "r") as f:
        for line in f:
            angle = line.strip("\n")
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
        recv_sock.send(f"{distances[i]}, ".encode())
    recv_sock.send(f"{distances[359]}\n".encode())

print("Shutting down...")
server_sock.close()
