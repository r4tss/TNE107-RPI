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

# DWM Process Code
DWMProcess = subprocess.Popen(["/home/pi/filterpy/bin/python", "-u", "/home/pi/TNE107-RPI/DWM.py"], stdout=subprocess.PIPE, stderr=open(os.devnull, 'wb'), text=True)
print(f"DWM PID: {DWMProcess.pid}")

# Open serial port to Arduino Nano
NANO = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
sleep(2)

BluetoothProcess = subprocess.Popen(["python", "-u", "/home/pi/TNE107-RPI/bt.py"], stdout=subprocess.PIPE, stderr=open(os.devnull, 'wb'), text=True)

# Waiting on connection
NANO.write(b"Bluetooth up\n")
print(BluetoothProcess.stdout.readline().strip())

# Connected?
# Bluetooth output
bto = BluetoothProcess.stdout.readline().strip()
print(bto)

newCommand = False

dwm = ""
x = 0
y = 0

oldX = 0
oldY = 0
forward = False
backward = False

curDir = 0
desDir = 0
normDir = 0

iteration = 0

if bto.find("Connected") != -1:
    nanoBtMessage = "Bluetooth connected " + bto[13:].translate({ord(c): None for c in ':'}) # Address to send to nano
    NANO.write(nanoBtMessage.encode())
    print(nanoBtMessage)

    # LIDAR Process Code
    LIDARProcess = subprocess.Popen(["/home/pi/TNE107-RPI/LIDARProg", "--channel", "--serial", "/dev/ttyUSB0", "460800"], stdout=open(os.devnull, 'wb'))
    print(f"LIDAR PID: {LIDARProcess.pid}")

    sleep(2)
    
    while bto != "1000":
        btReady, _, _ = select.select([BluetoothProcess.stdout], [], [], 0.0005)

        if btReady:
            bto = BluetoothProcess.stdout.readline().strip()
            newCommand = True
        else:
            newCommand = False

        dwmReady, _, _ = select.select([DWMProcess.stdout], [], [], 0.0005)

        if dwmReady:
            dwm = DWMProcess.stdout.readline().strip("\n")
            x, y = dwm.split(",")
            x = int(x)
            y = int(y)
            #print("Quality factor: " + qf)
            # if float(qf) > 80:

        if newCommand:
            print(f"Command: {bto}")
            if bto == "11":
                # Store current position => old pos
                # NANO.write(b"Forward\n")
                if forward == False:
                    oldX = x
                    oldY = y
                forward = True
                backward = False
            elif bto == "22":
                # Store current position => old pos
                # NANO.write(b"Backward\n")
                if backward == False:
                    oldX = x
                    oldY = y
                forward = False
                backward = True
            elif bto == "33":
                desDir = desDir - 90
                if desDir < 0:
                    desDir = desDir + 360

                curDir = desDir

                with open("angle.txt", "w") as f:
                    f.write(f"{desDir}" + '\n')
                    f.close()
                    
                NANO.write(b"Stop\n")
                sleep(0.1)    
                NANO.write(b"Right\n")
                sleep(0.95)
                NANO.write(b"Stop\n")
            elif bto == "44":
                desDir = desDir + 90
                if desDir >= 360:
                    desDir = desDir - 360

                curDir = desDir

                with open("angle.txt", "w") as f:
                    f.write(f"{desDir}" + '\n')
                    f.close()

                NANO.write(b"Stop\n")
                sleep(0.1)
                NANO.write(b"Left\n")
                sleep(0.9)
                NANO.write(b"Stop\n")
            elif bto == "55":
                desDir = desDir - 45
                if desDir < 0:
                    desDir = desDir + 360

                curDir = desDir

                with open("angle.txt", "w") as f:
                    f.write(f"{desDir}" + '\n')
                    f.close()

                NANO.write(b"Stop\n")
                sleep(0.1)
                NANO.write(b"Right\n")
                sleep(0.45)
                NANO.write(b"Stop\n")
            elif bto == "66":
                desDir = desDir + 45
                if desDir >= 360:
                    desDir = desDir - 360
                
                curDir = desDir

                with open("angle.txt", "w") as f:
                    f.write(f"{desDir}" + '\n')
                    f.close()
                    
                NANO.write(b"Stop\n")
                sleep(0.1)
                NANO.write(b"Left\n")
                sleep(0.45)
                NANO.write(b"Stop\n")
            elif bto == "420":
                NANO.write(b"Goal\n")
                print(NANO.readline())
                GPIO.output(LED, True)
                goal_read = False
                while goal_read == False:
                    goal_read = GPIO.input(PT)
                GPIO.output(LED, False)
            elif bto == "0":
                NANO.write(b"Stop\n")
                forward = False
                backward = False
            elif bto == "10":
                NANO.write(b"Stop\n")
                forward = False
                backward = False
                sleep(2)

                for i in range(30):
                    dwm = DWMProcess.stdout.readline().strip("\n")
                x, y = dwm.split(",")
                x = int(x)
                y = int(y)

                curDir = calcCurDir(x, y, oldX, oldY)

                adiff = calcAngleDiff(desDir, curDir)

                adjustAngle(adiff, forward, backward)

                forward = False
                backward = False

            elif bto == "98":
                GPIO.output(LED, True)
                sleep(1)
                GPIO.output(LED, False)

        with open("distances.txt", "r") as f:
            for line in f:
                a, d = line.split()
                a = int(a)
                d = int(d)

                if (a < 25 or a > 335) and (d > 0 and d < 300):
                    forward = False
                    if backward == False:
                        NANO.write(b"Stop\n")

                if ((a > 155 and a < 165) or (a > 195 and a < 205)) and (d > 0 and d < 300):
                    backward = False
                    if forward == False:
                        NANO.write(b"Stop\n")
    
        if forward:
            NANO.write(b"Forward\n")

        if backward:
            NANO.write(b"Backward\n")
        
        print(f"current pos ({x}, {y}) <- old pos ({oldX}, {oldY})")
        print(f"Current direction: {curDir}")
        print(f"Normalized direction: {normDir}")
        print(f"Desired direction: {desDir}")
        
        with open("angle.txt", "w") as f:
            f.write(f"{desDir}" + '\n')
            f.close()

        # Print current status (current command, heading? position? Could we include a cool progress bar? TO MISSION COMPLETETION?????)

    print("Terminating LIDAR process")
    os.kill(LIDARProcess.pid, signal.SIGINT)

    print("Terminating DWM Process")
    os.kill(DWMProcess.pid, signal.SIGINT)

print("Terminating Bluetooth Process")
os.kill(BluetoothProcess.pid, signal.SIGINT)

print("Terminating Serial port to Arduino Nano")
NANO.write(b"Closing down\n")
sleep(1)
NANO.close()


# Takes desired direction and current direction to get angle difference from desired direction
# Returns this angle difference with positive differences being left turns and negative ones being right turns
def calcAngleDiff(a1, a2):
    diff = a1 - a2

    if diff < -180:
        diff += 360

    return diff

def calcCurDir(x, y, xo, yo):
    curDir = math.atan2(y - yo, x - xo) * (180/math.pi)
    if curDir < 0:
        curDir = curDir + 360
    if curDir >= 360:
        curDir = curDir - 360

    return curDir

def adjustAngle(adiff, f, b):
    if f:
        if adiff > 10:
            print("Adjusting to the right")
            NANO.write(b"Right\n")
            sleep(abs(adiff) / 90)

        if normDir < -10:
            print("Adjusting to the left")
            NANO.write(b"Left\n")
            sleep(abs(adiff) / 90)
    else if b:
        if adiff < -10:
            print("Adjusting to the right")
            NANO.write(b"Right\n")
            sleep(abs(adiff) / 90)

        if normDir > 10:
            print("Adjusting to the left")
            NANO.write(b"Left\n")
            sleep(abs(adiff) / 90)

