import os
import subprocess
import signal
import serial
import select
from time import sleep
# import I2C_LCD_driver as LCD

# AGVlcd = LCD.lcd()

BluetoothProcess = subprocess.Popen(["python", "-u", "/home/pi/TNE107-RPI/bt.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

# Waiting on connection
# AGVlcd.lcd_display_string("Waiting for Bluetooth connection...", 1)
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

if bto.find("Connected") != -1:
    # AGVlcd.lcd_clear()
    # AGVlcd.lcd_display_string(bto)

    # Open serial port to Arduino Nano
    NANO = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

    # LIDAR Process Code
    LIDARProcess = subprocess.Popen(["./home/pi/TNE107-RPI/LIDARProg", "--channel", "--serial", "/dev/ttyUSB1", "460800"], stdout=open(os.devnull, 'wb'))
    print(f"LIDAR PID: {LIDARProcess.pid}")

    # DWM Process Code
    DWMProcess = subprocess.Popen(["python", "/home/pi/TNE107-RPI/DWM.py"], stdout=open(os.devnull, 'wb'))
    print(f"DWM PID: {DWMProcess.pid}")
    
    # sleep(3)
    
    while bto != "1000":
        ready, _, _ = select.select([BluetoothProcess.stdout], [], [], 0.001)

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

        # Print current status (current command, heading? position? Could we include a cool progress bar? TO MISSION COMPLETEION?????)

    
    print("Terminating Serial port to Arduino Nano")
    NANO.write(b"Stop\n")

    print("Terminating LIDAR process")
    os.kill(LIDARProcess.pid, signal.SIGINT)

    print("Terminating DWM Process")
    os.kill(DWMProcess.pid, signal.SIGINT)

print("Terminating Bluetooth Process")
os.kill(BluetoothProcess.pid, signal.SIGINT)

