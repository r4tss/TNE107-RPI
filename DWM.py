import serial
from time import sleep

with serial.Serial('/dev/ttyACM0', 115200, timeout = 1) as s:

    print(f"Opened serial port {s.name}")

    sleep(1)
    s.write(b"\r")
    sleep(0.1)
    s.write(b"\r")

    s.write(b'nis ')
    sleep(0.1)
    s.write(b'0x1234')
    sleep(0.1)
    s.write(b'\r')
    print(f"Set PAN ID to 0x1234")

    sleep(1)
    
    s.write(b'nmt')
    sleep(0.1)
    s.write(b'\r')
    print("Configured node as tag")

    sleep(1)

    s.write(b"\r")
    sleep(0.1)
    s.write(b"\r")

    sleep(2)

    s.write(b"aurs ")
    sleep(0.1)
    s.write(b"10 20")
    sleep(0.1)
    s.write(b'\r')
    print("Set update rate to 1 1")

    while True:
        sleep(0.1)
        s.write(b"apg")
        sleep(0.1)
        s.write(b"\r")

        str = f"{s.readline().decode('utf-8').strip('\n')}"

        if "apg: x:" in str:
            str = str.replace("apg: ", "")
            print(str)
            with open("posititon.txt", "w") as f:
                f.write(str + '\n')
                f.close()

print("Shutting down serial communication")
