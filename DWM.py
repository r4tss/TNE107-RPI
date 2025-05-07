import serial
import os
from time import sleep
from filterpy.kalman import UnscentedKalmanFilter
from filterpy.kalman import MerweScaledSigmaPoints
import numpy as np
import re
from collections import deque

def fx(x, t):
    return x

def hx(x):
    return x

x_mu = -0.02163601775523146
x_std = 0.07074315964054628
y_mu = 0.02645106742760512
y_std = 0.07415316805017082

points = MerweScaledSigmaPoints(n=2, alpha=1, beta=2, kappa=0)

kf = UnscentedKalmanFilter(dim_x=2, dim_z=2, dt=0.1, fx=fx, hx=hx, points=points)

# Initial position
kf.x = np.array([0., 0.])

# Initial error
kf.P *= 1000

# Noise matrix
kf.R = np.diag([25, 25])

kf.Q = np.eye(2)

position = deque([(0, 0)])

updRate = "1 1" # Active Idle

with serial.Serial('/dev/ttyACM0', 115200, timeout = 1) as s:

    # print(f"Opened serial port {s.name}")

    sleep(1)
    s.write(b"\r")
    sleep(0.1)
    s.write(b"\r")

    s.write(b'nis ')
    sleep(0.1)
    s.write(b'0x1234')
    sleep(0.1)
    s.write(b'\r')
    # print(f"Set PAN ID to 0x1234")

    sleep(1)
    
    s.write(b'nmt')
    sleep(0.1)
    s.write(b'\r')
    # print("Configured node as tag")

    sleep(1)

    s.write(b"\r")
    sleep(0.1)
    s.write(b"\r")

    sleep(2)

    s.write(b"aurs ")
    sleep(0.1)
    s.write(updRate.encode())
    sleep(0.1)
    s.write(b'\r')
    # print("Set update rate to " + updRate)

    sleep(0.1)
    s.write(b"lep")
    sleep(0.1)
    s.write(b"\r")
    sleep(0.1)

    for i in range(30):
        s.readline()

    for i in range(50):
        position.append((0, 0))
    
    while True:
        dstr = s.readline().decode('utf-8').strip('\n')

        if "POS," in dstr:
            dstr = re.sub('[^0-9,.]', '', dstr)
            _, x, y, z, qf = dstr.split(",")
            x = int(float(x) * 1000)
            y = int(float(y) * 1000)
            kf.predict()
            kf.update(np.array([x, y]))

            kfx = int(kf.x[0])
            kfy = int(kf.x[1])

            position.popleft()
            position.append((x, y))

            xmean = 0
            ymean = 0
            
            for p_i in position:
                xmean += p_i[0]
                ymean += p_i[1]

            xmean = int(xmean / 50)
            ymean = int(ymean / 50)

            with open("position_buf.txt", "w") as f:
                print(f"{kfx},{kfy}")
                f.write(f"{kfx},{kfy}\n")
            os.rename("position_buf.txt", "position.txt")

            with open("position_mean_buf.txt", "w") as f:
                #print(f"xmean: {xmean}, ymean: {ymean}")
                f.write(f"{xmean},{ymean}\n")
            os.rename("position_mean_buf.txt", "position_mean.txt")

print("Shutting down serial communication")
