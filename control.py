import bluetooth
import time

import termios
import tty
import sys

def get_input() -> str:
  
    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    key = sys.stdin.read(1)[0]
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN,filedescriptors)
  
    return key

pi = "B8:27:EB:D1:A5:A9"

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

print("Attempting to connect to %s..." % pi)

sock.connect((pi, 1))

print("Connected to %s." % pi)

input = "0"

while input != "a":
    input = get_input()

    print("Sending: %s" % input)
    if input == "i":
        sock.send("11")
    elif input == "j":
        sock.send("44")
    elif input == "l":
        sock.send("33")
    elif input == "k":
        sock.send("22")
    else:
        sock.send("0")

    read = sock.recv(1024)
    read = read.decode("utf-8").strip('\n')
    print("Received: '%s'" % read )

    time.sleep(0.1)

print("Sending: %s" % input)
sock.send(input)

read = sock.recv(1024)
read = read.decode("utf-8").strip('\n')
print("Received: '%s'" % read )

print("Shutting down...")

sock.close()
