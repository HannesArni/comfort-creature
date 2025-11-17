import time

import serial

# Adjust this to your port
PORT = "/dev/tty.usbserial-210"  # e.g. "COM5" on Windows, "/dev/ttyUSB0" or "/dev/ttyACM0" on Linux

ser = serial.Serial(PORT, 115200, timeout=1)
time.sleep(5)  # allow Arduino to reset

start_byte = 0xAA
header = 0x02294504
payload = 0x0000000000000000

frame = (
    start_byte.to_bytes(1, byteorder="big")
    + header.to_bytes(4, byteorder="big")
    + payload.to_bytes(8, byteorder="big")
)

print("Sending frame bytes:", frame.hex())
ser.write(frame)
ser.write(frame)
ser.write(frame)
time.sleep(1)
while True:
    line = ser.readline()
    if not line:
        break
    print("Arduino:", line.decode(errors="ignore").strip())

print("Sending frame bytes:", frame.hex())
ser.write(frame)
time.sleep(1)

while True:
    line = ser.readline()
    if not line:
        break
    print("Arduino:", line.decode(errors="ignore").strip())

ser.close()
