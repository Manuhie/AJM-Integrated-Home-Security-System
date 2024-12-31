import serial
from time import sleep
arduino = serial.Serial(port='COM3', baudrate = 500000, timeout=1)
arduino.write(bytes("CHECK", 'utf-8'))
sleep(0.1)
arduino.write(bytes("Welcome Manuhie!", 'utf-8'))
