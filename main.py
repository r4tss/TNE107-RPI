import os
import subprocess
import signal
import serial
import select
from time import sleep

# Open serial port to Arduino Nano
NANO = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
sleep(2)

BluetoothProcess = subprocess.Popen(["python", "-u", "/home/pi/TNE107-RPI/bt.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

# Waiting on connection
NANO.write(b"Bluetooth up\n")
print(BluetoothProcess.stdout.readline().strip())

# Connected?
# Bluetooth output
bto = BluetoothProcess.stdout.readline().strip()
print(bto)

newCommand = False
rightTurnIndex = 50
rightTurn = 0
leftTurnIndex = 20
leftTurn = 0

dwm = ""

if bto.find("Connected") != -1:
    nanoBtMessage = "Bluetooth connected " + bto[13:].translate({ord(c): None for c in ':'}) # Address to send to nano
    NANO.write(nanoBtMessage.encode())
    print(nanoBtMessage)

    # LIDAR Process Code
    LIDARProcess = subprocess.Popen(["/home/pi/TNE107-RPI/LIDARProg", "--channel", "--serial", "/dev/ttyUSB0", "460800"], stdout=open(os.devnull, 'wb'))
    print(f"LIDAR PID: {LIDARProcess.pid}")

    # DWM Process Code
    DWMProcess = subprocess.Popen(["python", "/home/pi/TNE107-RPI/DWM.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
    print(f"DWM PID: {DWMProcess.pid}")
    
    while bto != "1000":
        btReady, _, _ = select.select([BluetoothProcess.stdout], [], [], 0.0005)

        if btReady:
            bto = BluetoothProcess.stdout.readline().strip()
            newCommand = True
        else:
            newCommand = False

        dwmReady, _, _ = select.select([DWMProcess.stdout], [], [], 0.0005)

        if dwmReady:
            dwm = DWMProcess.stdout.readline()

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
                # Store current position => old pos
                NANO.write(b"Forward\n")
            elif bto == "22":
                # Store current position => old pos
                NANO.write(b"Backward\n")
            elif bto == "33":
                # NANO.write(b"Right\n")
                rightTurn = rightTurnIndex
                leftTurn = 0
            elif bto == "44":
                # NANO.write(b"Left\n")
                leftTurn = leftTurnIndex
                rightTurn = 0
            else:
                # Store current position => cur pos
                # Calculate angle from old pos, a = math.atan2(y, x) + math.pi
                NANO.write(b"Stop\n")

        # Print current status (current command, heading? position? Could we include a cool progress bar? TO MISSION COMPLETEION?????)

    
    print("Terminating Serial port to Arduino Nano")
    NANO.write(b"Closing down\n")
    sleep(1)
    NANO.close()

    print("Terminating LIDAR process")
    os.kill(LIDARProcess.pid, signal.SIGINT)

    print("Terminating DWM Process")
    os.kill(DWMProcess.pid, signal.SIGINT)

print("Terminating Bluetooth Process")
os.kill(BluetoothProcess.pid, signal.SIGINT)

