import serial
from time import sleep
from filterpy.kalman import KalmanFilter
import numpy as np
import re
from collections import deque

# x_mu = -0.02163601775523146
# x_std = 0.07074315964054628
# y_mu = 0.02645106742760512
# y_std = 0.07415316805017082

# kf = KalmanFilter(dim_x=2, dim_z=2, alpha=10)

# # Initial position
# kf.x = np.array([[0.],
#                  [0.]])

# # State transition matrix
# kf.F = np.array([[1., 0.],
#                  [0., 1.]])

# # Measurement function
# kf.H = np.array([[1., 0.],
#                  [0., 1.]])

# # Covariance matrix
# kf.P = np.array([[x_std**2, 0.],
#                  [0., y_std**2]])

# kf.R = np.array([[x_std**2, 0.],
#                  [0., y_std**2]])

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

    for i in range(10):
        s.readline()

    for i in range(10):
        print(i)
        position.append((0, 0))
    
    while True:
        dstr = s.readline().decode('utf-8').strip('\n')

        if "POS," in dstr:
            dstr = re.sub('[^0-9,.]', '', dstr)
            _, x, y, z, qf = dstr.split(",")
            x = int(float(x) * 1000)
            y = int(float(y) * 1000)
            # kf.predict()
            # kf.update(np.array([[x],
            #                     [y]]))

            # x = int(kf.x[0] * 1000)
            # y = int(kf.x[1] * 1000)

            position.popleft()
            position.append((x, y))

            x = 0
            y = 0
            
            for p_i in position:
                x += p_i[0]
                y += p_i[1]

            x = x / 10
            y = y / 10

            with open("position.txt", "w") as f:
                print(f"{x},{y}")
                f.write(f"{x},{y}\n")
                f.close()

print("Shutting down serial communication")
