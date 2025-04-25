# TNE107-RPI

## control.py

This control program is not needed for operation and is strictly used to test implementation. 

## bt.py

This program controls the Bluetooth behaviour of the system. 

## DWM.py

This program interfaces with the DWM1001 UWB transciever via serial to get location data.

## LIDAR

This program interfaces with the SLAMTEC RPLIDAR C1. To use this there are a couple steps to take.

1. Compile the SDK in its respective folder.
2. Compile the actual LIDAR program and move it from output to the source directory with name `LIDARProg`.

## main.py

This program starts all the other programs at the correct times for communication to occur and for data handling to be done properly. This program is run as a systemd service on the Raspberry Pi. 