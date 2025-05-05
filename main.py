import os
import subprocess
import signal
import serial
import select
from time import sleep
import math
import RPi.GPIO as GPIO

LED = 17 # Light emitting diode
PT = 27 # Phototransistor

GPIO.setmode(GPIO.BCM)
GPIO.setup(PT, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, False)

# Open serial port to Arduino Nano
NANO = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
sleep(2)

BluetoothProcess = subprocess.Popen(["python", "-u", "/home/pi/TNE107-RPI/bt.py"], stdout=subprocess.PIPE, text=True)

# Waiting on connection
NANO.write(b"Bluetooth up\n")
print(BluetoothProcess.stdout.readline().strip())

# Connected?
# Bluetooth output
bto = BluetoothProcess.stdout.readline().strip()
print(bto)

newCommand = False
rightTurnIndexN = 100
rightTurnIndexF = 50
rightTurnIndexR = 0
rightTurn = 0
leftTurnIndexN = 100
leftTurnIndexF = 50
leftTurn = 0

angle = 0.0

dwm = ""
x = ""
y = ""

curX = 0
curY = 0
oldX = 0
oldY = 0
backward = False

curDir = 0
desDir = 0

if bto.find("Connected") != -1:
    GPIO.output(LED, True)
    nanoBtMessage = "Bluetooth connected " + bto[13:].translate({ord(c): None for c in ':'}) # Address to send to nano
    NANO.write(nanoBtMessage.encode())
    print(nanoBtMessage)

    # LIDAR Process Code
    LIDARProcess = subprocess.Popen(["/home/pi/TNE107-RPI/LIDARProg", "--channel", "--serial", "/dev/ttyUSB0", "460800"], stdout=open(os.devnull, 'wb'))
    print(f"LIDAR PID: {LIDARProcess.pid}")

    # DWM Process Code
    DWMProcess = subprocess.Popen(["python", "-u", "/home/pi/TNE107-RPI/DWM.py"], stdout=subprocess.PIPE, text=True)
    print(f"DWM PID: {DWMProcess.pid}")

    sleep(5)
    
    while bto != "1000":
        #print(GPIO.input(PT))
        btReady, _, _ = select.select([BluetoothProcess.stdout], [], [], 0.0005)

        if btReady:
            bto = BluetoothProcess.stdout.readline().strip()
            newCommand = True
        else:
            newCommand = False

        dwmReady, _, _ = select.select([DWMProcess.stdout], [], [], 0.0005)

        if dwmReady:
            dwm = DWMProcess.stdout.readline().strip("\n")
            x, y, z, qf = dwm.split(",")
            #print("Quality factor: " + qf)
            # if float(qf) > 80:
            print(x + ", " + y)

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
            print(f"Command: {bto}")
            if bto == "11":
                # Store current position => old pos
                oldX = float(x) * 1000
                oldY = float(y) * 1000
                backward = False
                NANO.write(b"Forward\n")
            elif bto == "22":
                oldX = float(x) * 1000
                oldY = float(y) * 1000
                backward = True
                # Store current position => old pos
                NANO.write(b"Backward\n")
            elif bto == "33":
                desDir = desDir - 90
                if desDir < 360:
                    desDir = desDir + 360

                curDir = desDir
                    
                NANO.write(b"Right\n")
                sleep(0.95)
                NANO.write(b"Stop\n")
            elif bto == "44":
                desDir = desDir + 90
                if desDir >= 360:
                    desDir = desDir - 360

                curDir = desDir
                    
                NANO.write(b"Left\n")
                sleep(0.9)
                NANO.write(b"Stop\n")
            elif bto == "55":
                desDir = desDir - 45
                if desDir < 360:
                    desDir = desDir + 360

                curDir = desDir
                    
                NANO.write(b"Left\n")
                sleep(0.45)
                NANO.write(b"Stop\n")
            elif bto == "66":
                desDir = desDir + 45
                if desDir >= 0:
                    desDir = desDir - 360
                
                curDir = desDir
                
                NANO.write(b"Left\n")
                sleep(0.45)
                NANO.write(b"Stop\n")
            elif bto == "420":
                print("reset")
                desDir = 0
            else:
                # Store current position => cur pos
                # curX = float(x) * 1000
                # curY = float(y) * 1000

                # oldDir = curDir

                # curDir = (math.atan2(curY - oldY, curX - oldX) + math.pi) * (180/math.pi)
                # if backward == True:
                #     a = a - 180
                print(f"Current direction: {curDir}")
                NANO.write(b"Stop\n")

        with open("angle.txt", "w") as f:
            f.write(f"{curDir}" + '\n')
            f.close()

        

        # Print current status (current command, heading? position? Could we include a cool progress bar? TO MISSION COMPLETETION?????)

    
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

# def calc_turn(desiredDirection, currentDirection):
