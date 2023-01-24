from subprocess import Popen, PIPE
import serial
from time import sleep

def connectToSensor(macAddress, rfcommString):
    Popen(['sudo', 'rfcomm', 'connect', rfcommString, macAddress, '1', '&'])

def disconnectSensor(rfcommString):
    Popen(['sudo', 'rfcomm', 'release', rfcommString])

#connectToSensor('98:D3:11:FC:5D:34', '/dev/rfcomm1')
connectToSensor('98:D3:51:FD:F9:E9', '/dev/rfcomm1')   
sleep(5)
sensor1 = serial.Serial("/dev/rfcomm1", baudrate=9600)

while True:
    #print ("Sending on")
    #sensor1.write(b'ON')
    #sleep(5)
    #print ("Sending off")
    #sensor1.write(b'OFF')
    msg = sensor1.readline()
    print(msg.decode("utf-8"))
    sleep(5)
    #break;

disconnectSensor("/dev/rfcomm1")