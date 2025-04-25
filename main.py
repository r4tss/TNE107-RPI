import os
import subprocess
import signal
import serial
import select
from time import sleep

BluetoothProcess = subprocess.Popen(["python", "-u", "bt.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

# Waiting on connection
print(BluetoothProcess.stdout.readline().strip())

# Connected?
# Bluetooth output
bto = BluetoothProcess.stdout.readline().strip()
print(bto)

newCommand = False
rightTurnIndex = 5
rightTurn = 0
leftTurnIndex = 2
leftTurn = 0

if bto.find("Connected") != -1:
    # Open serial port to Arduino Nano
    NANO = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

    # LIDAR Process Code
    LIDARProcess = subprocess.Popen(["./LIDARProg", "--channel", "--serial", "/dev/ttyUSB1", "460800"], stdout=open(os.devnull, 'wb'))
    print(f"LIDAR PID: {LIDARProcess.pid}")

    # DWM Process Code
    DWMProcess = subprocess.Popen(["python", "DWM.py"], stdout=open(os.devnull, 'wb'))
    print(f"DWM PID: {DWMProcess.pid}")
    
    while bto != "1000":
        ready, _, _ = select.select([BluetoothProcess.stdout], [], [], 0.01)

        if ready:
            bto = BluetoothProcess.stdout.readline().strip()
            newCommand = True
        else:
            newCommand = False

        # Send commands to Arduino based on bto
        if rightTurn > 0:
            NANO.write(b"Right\n")
            rightTurn = rightTurn - 1
            if rightTurn == 0:
                NANO.write(b"00")

        if leftTurn > 0:
            NANO.write(b"Left\n")
            leftTurn = leftTurn - 1
            if leftTurn == 0:
                NANO.write(b"00")

        if newCommand:
            if bto == "11":
                NANO.write(b"Forward\n")
            elif bto == "22":
                NANO.write(b"Backward\n")
            elif bto == "33":
                # NANO.write(b"Right\n")
                rightTurn = rightTurnIndex
                leftTurn = 0
            elif bto == "44":
                # NANO.write(b"Left\n")
                leftTurn = leftTurnIndex
                rightTurn = 0
            elif bto == "0":
                NANO.write(b"Stop\n")

    
    print("Terminating Serial port to Arduino Nano")
    NANO.write(b"Stop\n")

    print("Terminating LIDAR process")
    os.kill(LIDARProcess.pid, signal.SIGINT)

    print("Terminating DWM Process")
    os.kill(DWMProcess.pid, signal.SIGINT)

print("Terminating Bluetooth Process")
os.kill(BluetoothProcess.pid, signal.SIGINT)

