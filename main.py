import os
import subprocess
import signal
import serial
import select
from time import sleep
import math
import RPi.GPIO as GPIO

# Takes desired direction and current direction to get angle difference from desired direction
# Returns this angle difference with positive differences being left turns and negative ones being right turns
def calcAngleDiff(a1, a2):
    diff = a1 - a2

    if diff < -180:
        diff += 360

    # print(f"Angle diff: {diff}")
    return diff

def calcCurDir(x, y, xo, yo):
    curDir = math.atan2(y - yo, x - xo) * (180/math.pi)
    if curDir < 0:
        curDir = curDir + 360
    if curDir >= 360:
        curDir = curDir - 360

    # print(f"Current angle: {curDir}")
    return curDir

def adjustAngle(adiff, f, b):
    if f == True:
        # print("Going forward")
        if adiff < 0:
            print("Adjusting to the right")
            NANO.write(b"Right\n")
            sleep(abs(adiff) / 90)
            NANO.write(b"Stop\n")
        elif adiff > 0:
            print("Adjusting to the left")
            NANO.write(b"Left\n")
            sleep(abs(adiff) / 90)
            NANO.write(b"Stop\n")
    elif b == True:
        # print("Going backward")
        if adiff < 0:
            adiff += 180
            print(f"Adjusting to the left {adiff}")
            NANO.write(b"Left\n")
            sleep(abs(adiff) / 90)
            NANO.write(b"Stop\n")
        elif adiff > 0:
            adiff -= 180
            print(f"Adjusting to the right {adiff}")
            NANO.write(b"Right\n")
            sleep(abs(adiff) / 90)
            NANO.write(b"Stop\n")

def writeAngleToFile(a):
    with open("angle_buf.txt", "w") as f:
        f.write(f"{a}" + '\n')
    os.rename("angle_buf.txt", "angle.txt")

LED = 17 # Light emitting diode
PT = 27 # Phototransistor

GPIO.setmode(GPIO.BCM)
GPIO.setup(PT, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, False)

# DWM Process Code
DWMProcess = subprocess.Popen(["/home/pi/filterpy/bin/python", "-u", "/home/pi/TNE107-RPI/DWM.py"], stdout=subprocess.PIPE, text=True) # stderr=open(os.devnull, 'wb'),
print(f"DWM PID: {DWMProcess.pid}")

# Open serial port to Arduino Nano
NANO = serial.Serial('/dev/ttyACM0', 115200, timeout=30)
sleep(2)

BluetoothProcess = subprocess.Popen(["python", "-u", "/home/pi/TNE107-RPI/bt.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True) # stderr=open(os.devnull, 'wb'),


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

obstructF = False
obstructB = False

curDir = 0
desDir = 0
normDir = 0

writeAngleToFile(desDir)

iteration = 1
delay = 100 # Delay status command to every 20 loops

calibrationBudget = 20

if bto.find("Connected") != -1:
    nanoBtMessage = "Bluetooth connected " + bto[13:].translate({ord(c): None for c in ':'}) # Address to send to nano
    NANO.write(nanoBtMessage.encode())
    print(nanoBtMessage)

    # LIDAR Process Code
    LIDARProcess = subprocess.Popen(["/home/pi/TNE107-RPI/LIDARProg", "--channel", "--serial", "/dev/ttyUSB0", "460800"], stdout=open(os.devnull, 'wb'))
    print(f"LIDAR PID: {LIDARProcess.pid}")

    sleep(2)
    
    while bto != "1000":
        i = 0

        btReady = bool(select.select([BluetoothProcess.stdout], [], [], 0.0005)[0])

        if btReady:
            bto = BluetoothProcess.stdout.readline().strip()
            newCommand = True
        else:
            newCommand = False

        dwmReady = bool(select.select([DWMProcess.stdout], [], [], 0.0005)[0])

        if dwmReady:
            while dwmReady:
                dwmReady = bool(select.select([DWMProcess.stdout], [], [], 0.05)[0])
                dwm = DWMProcess.stdout.readline().strip("\n")
            x, y = dwm.split(",")
            x = int(x)
            y = int(y)
            #print("Quality factor: " + qf)
            # if float(qf) > 80:

        if newCommand:
            print(f"Command: {bto}")
            if bto == "11": # Go forward
                if forward == False:
                    oldX = x
                    oldY = y
                forward = True
                backward = False
                
            elif bto == "22": # Go backward
                if backward == False:
                    oldX = x
                    oldY = y
                forward = False
                backward = True
                
            elif bto == "33": # Turn right 90 degrees
                desDir = desDir - 90
                if desDir < 0:
                    desDir = desDir + 360

                curDir = desDir

                writeAngleToFile(desDir)
                    
                NANO.write(b"Stop\n")
                sleep(0.1)    
                NANO.write(b"Right\n")
                NANO.write(f"Current status {xstatus} {ystatus} {dirstatus}\n".encode())
                sleep(1)
                NANO.write(b"Stop\n")
                
            elif bto == "44": # Turn left 90 degrees
                desDir = desDir + 90
                if desDir >= 360:
                    desDir = desDir - 360

                curDir = desDir

                writeAngleToFile(desDir)

                NANO.write(b"Stop\n")
                sleep(0.1)
                NANO.write(b"Left\n")
                NANO.write(f"Current status {xstatus} {ystatus} {dirstatus}\n".encode())
                sleep(1)
                NANO.write(b"Stop\n")
                
            elif bto == "55": # Turn right 45 degrees
                desDir = desDir - 45
                if desDir < 0:
                    desDir = desDir + 360

                curDir = desDir

                writeAngleToFile(desDir)

                NANO.write(b"Stop\n")
                sleep(0.1)
                NANO.write(b"Right\n")
                NANO.write(f"Current status {xstatus} {ystatus} {dirstatus}\n".encode())
                sleep(0.5)
                NANO.write(b"Stop\n")
                
            elif bto == "66": # Turn left 45 degrees
                desDir = desDir + 45
                if desDir >= 360:
                    desDir = desDir - 360
                
                curDir = desDir

                writeAngleToFile(desDir)
                    
                NANO.write(b"Stop\n")
                sleep(0.1)
                NANO.write(b"Left\n")
                NANO.write(f"Current status {xstatus} {ystatus} {dirstatus}\n".encode())
                sleep(0.5)
                NANO.write(b"Stop\n")
                
            elif bto == "0": # Stop
                NANO.write(b"Stop\n")
                forward = False
                backward = False
                
            elif bto == "10": # Stop and find current position
                dwmReady = True
                while dwmReady:
                    dwmReady, _, _ = select.select([DWMProcess.stdout], [], [], 0.0005)
                    dwm = DWMProcess.stdout.readline().strip("\n")

                NANO.write(b"Stop\n")

                xmean = 0
                ymean = 0
                # Change number of iterations to change wait time
                # Readings come every 0.1 seconds, so 30 iterations
                # means 3 second delay. 
                for i in range(calibrationBudget):
                    dwm = DWMProcess.stdout.readline().strip("\n")
                    x, y = dwm.split(",")
                    x = int(x)
                    y = int(y)
                    
                    xmean += x
                    ymean += y

                x = xmean / calibrationBudget
                y = ymean / calibrationBudget
                
                print(f"Desired direction {desDir}")
                curDir = calcCurDir(x, y, oldX, oldY)

                adiff = calcAngleDiff(desDir, curDir)

                adjustAngle(adiff, forward, backward)

                forward = False
                backward = False

            elif "98" in bto:
                NANO.write(b"Stop\n")

                dwmReady = True
                while dwmReady:
                    dwmReady = bool(select.select([DWMProcess.stdout], [], [], 0.05)[0])
                    dwm = DWMProcess.stdout.readline().strip("\n")

                xmean = 0
                ymean = 0

                for i in range(calibrationBudget):
                    dwm = DWMProcess.stdout.readline().strip("\n")
                    x, y = dwm.split(",")
                    x = int(x)
                    y = int(y)
                    
                    xmean += x
                    ymean += y

                x = xmean / calibrationBudget
                y = ymean / calibrationBudget
                oldX = x
                oldY = y

                curDir = desDir
                # curDir = calcCurDir(x, y, oldX, oldY)
                
                _, gx, gy, gDir = bto.split()

                gx = int(gx)
                gy = int(gy)
                gDir = int(gDir)

                print(f"AGV: (x:{x}, y:{y}, dir:{curDir})")
                print(f"goal: (x:{gx}, y:{gy}, dir:{gDir})")

                # Flips gDir so that N = 270 => 90 etc.
                # gDir += 180
                # if gDir > 360:
                #     gDir -= 360

                gx += 15 * math.cos(math.radians(gDir))
                gy += 15 * math.sin(math.radians(gDir))

                tapeDir = calcCurDir(gx, gy, x, y)

                print(f"goal tape end: (x:{gx}, y:{gy}, dir:{tapeDir})")

                adiff = calcAngleDiff(curDir, tapeDir)

                print(f"Angle diff: {adiff}")

                # We want to go forward towards the goal
                adjustAngle(-adiff, True, False)

                # NANO.write(b"Forward\n")
                # sleep(1)

                # NANO.write(b"Stop\n")
                # sleep(1)

                # xmean = 0
                # ymean = 0

                # dwmReady = True
                # while dwmReady:
                #     dwmReady = bool(select.select([DWMProcess.stdout], [], [], 0.05)[0])
                #     DWMProcess.stdout.readline().strip("\n")

                # i = 0
                # for i in range(calibrationBudget):
                #     dwm = DWMProcess.stdout.readline().strip("\n")
                #     x, y = dwm.split(",")
                #     x = int(x)
                #     y = int(y)
                #     
                #     xmean += x
                #     ymean += y

                # x = xmean / calibrationBudget
                # y = ymean / calibrationBudget

                # curDir = calcCurDir(x, y, oldX, oldY)

                # tapeDir = calcCurDir(gx, gy, x, y)

                # adiff = calcAngleDiff(curDir, tapeDir)

                # print(f"Angle diff: {adiff}")

                # # We want to go forward towards the goal
                # adjustAngle(-adiff, True, False)
                
                # Start goal communication
                NANO.write(b"Start goal\n")

                # Wait for AGV to have detected something in front of it.
                print(NANO.readline().decode("utf8-").strip())

                # AGV has now started wiggling and we check the phototransistor
                # to see if the LED has triggered the goal. 
                GPIO.output(LED, True)
                goal_read = False
                while goal_read == False:
                    goal_read = GPIO.input(PT)
                    BluetoothProcess.stdin.write("98\n")
                    BluetoothProcess.stdin.flush()
                    sleep(0.1)
                GPIO.output(LED, False)
                NANO.write(b"Found goal\n")

                curDir = gDir
                writeAngleToFile(curDir)

                BluetoothProcess.stdin.write("99\n")
                BluetoothProcess.stdin.flush()
                print("Sent bluetooth 99")

        # Check LIDAR data to see if anything is in front or behind AGV
        with open("distances.txt", "r") as f:
            for line in f:
                a, d = line.split()
                a = int(a)
                d = int(d)

                if (a < 25 or a > 335) and (d > 0 and d < 200):
                    forward = False
                    if backward == False:
                        obstructF = True
                        NANO.write(b"Stop\n")

                if ((a > 155 and a < 165) or (a > 195 and a < 205)) and (d > 0 and d < 200):
                    backward = False
                    if forward == False:
                        obstructB = True
                        NANO.write(b"Stop\n")
    
        if forward:
            NANO.write(b"Forward\n")

        if backward:
            NANO.write(b"Backward\n")

        if obstructF:
            print("Obstruction front")
            obstructF = False
            NANO.write(b"Backward\n")
            sleep(0.5)
            NANO.write(b"Stop\n")

        if obstructB:
            print("Obstruction back")
            obstructB = False
            NANO.write(b"Forward\n")
            sleep(0.5)
            NANO.write(b"Stop\n")

        xstatus = str(x).zfill(4)
        ystatus = str(y).zfill(4)
        dirstatus = str(int(curDir)).zfill(3)
        if iteration > delay:
            NANO.write(f"Current status {xstatus} {ystatus} {dirstatus}\n".encode())
            print(f"Current status {xstatus} {ystatus} {dirstatus}")
            iteration = 0
        iteration += 1

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
