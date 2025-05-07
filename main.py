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
DWMProcess = subprocess.Popen(["/home/pi/venv/bin/python", "-u", "/home/pi/TNE107-RPI/DWM.py"], stdout=subprocess.PIPE, text=True)
print(f"DWM PID: {DWMProcess.pid}")

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
                NANO.write(b"Forward\n")
                if forward == False:
                    oldX = x
                    oldY = y
                    sleep(2)
                forward = True
                backward = False
            elif bto == "22":
                # Store current position => old pos
                NANO.write(b"Backward\n")
                if backward == False:
                    oldX = x
                    oldY = y
                    sleep(2)
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

                NANO.write(b"Left\n")
                sleep(0.45)
                NANO.write(b"Stop\n")
            elif bto == "420":
                print("reset")
                desDir = 0
            elif bto == "0":
                NANO.write(b"Stop\n")
                forward = False
                backward = False
            elif bto == "10":
                NANO.write(b"Stop\n")
                forward = False
                backward = False
            elif bto == "98":
                GPIO.output(LED, True)
                sleep(1)
                GPIO.output(LED, False)
                
            

        curDir = math.atan2(y - oldY, x - oldX) * (180/math.pi)
        if curDir < 0:
            curDir = curDir + 360
        if curDir >= 360:
            curDir = curDir - 360


        normDir = (desDir - curDir) % 360
        if normDir > 180:
            normDir -= 360

        if forward:
            NANO.write(b"Forward\n")
            
            # if normDir > 10:
            #     print("Adjusting to the left")
            #     NANO.write(b"Left\n")
            #     sleep(normDir / 1000)

            # if normDir < -10:
            #     print("Adjusting to the right")
            #     NANO.write(b"Right\n")
            #     sleep(normDir / 1000)


        if backward:
            NANO.write(b"Backward\n")
        
        sleep(0.1)
        print(f"current pos ({x}, {y}) -> old pos ({oldX}, {oldY})")
        print(f"Current direction: {curDir}")
        print(f"Normalized direction: {normDir}")
        print(f"Desired direction: {desDir}")
        
        with open("angle.txt", "w") as f:
            f.write(f"{desDir}" + '\n')
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
