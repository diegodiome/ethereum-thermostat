import bluetooth
import deploy_contracts as et
from sensor import Sensor
from heater import Heater
from time import sleep
from subprocess import Popen, PIPE
import serial
from threading import Thread
import random


sensors = []
sensors_enabled_filter = []
sensors_disabled_filter = []

def addSensor(newSensor):
    sensors.append(newSensor)

def receiveMessages():
  addPort()
  server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
  
  port = 1
  server_sock.bind(("",port))
  server_sock.listen(1)
  
  while True:
      print("listening")
      client_sock,address = server_sock.accept()
      print ("Accepted connection from " + str(address))
      try:
          while True:
              data = client_sock.recv(1024)
              if not data:
                  break
              print ("received [%s]" % data)
              analyzeMessage(data, client_sock)
      except OSError:
         print("Smartphone disconnected")
         client_sock.close()
         
  server_sock.close()
  
def sendMessageTo(sock, message):
  sock.send(message)

def addPort():
    Popen(['sudo', 'sdptool', 'add', 'SP'])

def analyzeMessage(data, sock):
  data = data.decode("utf-8")
  if(data == "getdevices"):
    sendMessageTo(sock, lookUpNearbyBluetoothDevices())
  elif(data == "ready"):
    readySensors(sock)
  else:
    subdata = data.split("#")
    if(subdata[0] == "adds"):
        #deploy sensor
        macAddress = subdata[1].split("&")[0]
        thermostatAddress = subdata[1].split("@")[1]
        contractAddress = et.deployNewSensor(thermostatAddress)
        index = len(sensors)
        contracts = et.web3.eth.contract(address=contractAddress, abi=et.readAbi("sensor.json"))
        sendMessageTo(sock, "ok#" + macAddress + "&" + contractAddress)
        addSensor(Sensor(contracts, macAddress, index, connectToSensor(macAddress, index + 1)))
        print("Serial port with sensor " + macAddress + " opened!")

def connectToSensor(macAddress, index):
    rfcommString = '/dev/rfcomm' + str(index)
    Popen(['sudo', 'rfcomm', 'connect', rfcommString, macAddress, '1', '&'])
    sleep(4)
    return serial.Serial(rfcommString, baudrate=9600)

def readTemperature(port):
    actualTemp = port.readline().decode('utf-8')
    return actualTemp.split("\n")[0]

def disconnectSensor(rfcommString):
    Popen(['sudo', 'rfcomm', 'release', rfcommString])

def lookUpNearbyBluetoothDevices():
  nearby_devices = bluetooth.discover_devices()
  response = ""
  if(len(nearby_devices) == 0):
      response = "nodevice"
      print('No device found')
  for device_addr in nearby_devices:
      if('Sensor' in str(bluetooth.lookup_name(device_addr))):
          print (str(bluetooth.lookup_name(device_addr)) + " [" + str(device_addr) + "]")
          response = response + str(bluetooth.lookup_name(device_addr)) + "&" + str(device_addr) + "#"
  return response

def readySensors(sock):
    sleep(5)
    for sensor in sensors:
        et.initializeTemperature(sensor.contract, 20)
    sendMessageTo(sock, "ready")
    initEvents()

def sendTemperature(sensor):
    sleep(2)
    if(et.activationsCall(sensor.contract, int('-937354887'))):
        try:
            et.communicateTemperature(sensor.contract, int(float(readTemperature(sensor.port))))
            print("Sensor" + str(sensor.id) + " : " + sensor.contract.address + " comunicated his temperature!")
        except:
            print("Sensor" + str(sensor.id) + " : " + sensor.contract.address + " error while communicating temperature!")
    else:
        print("Sensor" + str(sensor.id) + " : " + sensor.contract.address + " can't communicate temperature!")
        
  
def initEvents():
    for sensor in sensors:
        sensors_enabled_filter.append(sensor.contract.events.enabled.createFilter(fromBlock='latest'))
        sensors_disabled_filter.append(sensor.contract.events.disabled.createFilter(fromBlock='latest'))
    
    while True:
        for sensor in sensors:
            sendTemperature(sensor)
        sleep(40)


receiveMessages()

def demoMode():
    contractAddress0 = '0x4eF37F30b9F3aB31092d320C0D94b1ce15a1EBa6'
    contractAddress1 = '0x15Db0fbA4fe7DCb94F4b93f0ecc07FBb7EE52131'
    contract0 = et.web3.eth.contract(address=contractAddress0, abi=et.readAbi("sensor.json"))
    contract1 = et.web3.eth.contract(address=contractAddress1, abi=et.readAbi("sensor.json"))
    sensors.append(Sensor(contract0, '98:D3:91:FD:BC:1D', 0, connectToSensor('98:D3:91:FD:BC:1D', 1)))
    sensors.append(Sensor(contract1, '98:D3:51:FD:F9:E9', 1, connectToSensor('98:D3:51:FD:F9:E9', 2)))
    initEvents()

#demoMode()
      