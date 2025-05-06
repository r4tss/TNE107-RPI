import serial
from time import sleep
from filterpy.kalman import KalmanFilter

x_mu = -0.02163601775523146
x_std = 0.07074315964054628
y_mu = 0.02645106742760512
y_std = 0.07415316805017082

kf = KalmanFilter(dim_x=2, dim_z=2)

# Initial position
kf.x = np.array([0.],
                [0.])

# State transition matrix
kf.F = np.array([1., 0.],
                [0., 1.])

# Measurement function
kf.H = np.array([1., 0.],
                [0., 1.])

# Covariance matrix
kf.P = np.array([x_std**2, 0.],
                [0., y_std**2])

kf.R = np.array([x_mu, 0.],
                [0., y_mu])

updRate = "10 10" # Active Idle

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

    while True:
        str = s.readline().decode('utf-8').strip('\n')

        if "POS," in str:
            str = str.replace("POS,", "")
            print(str)
            with open("position.txt", "w") as f:
                f.write(str + '\n')
                f.close()

print("Shutting down serial communication")
