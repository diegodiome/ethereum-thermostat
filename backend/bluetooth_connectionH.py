import bluetooth
import deploy_contracts as et
from heater import Heater
from time import sleep
from subprocess import Popen, PIPE
import serial
from threading import Thread


heaters = []
heaters_enabled_filter = []
heaters_disabled_filter = []
heaters_status_filter = []

def addHeater(newHeater):
    heaters.append(newHeater)

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
        #deploy heater
        macAddress = subdata[1].split("&")[0]
        thermostatAddress = subdata[1].split("@")[1]
        contractAddress = et.deployNewHeater(thermostatAddress)
        sendMessageTo(sock, "ok#" + macAddress + "&" + contractAddress)
        index = len(sensors)
        contracth = et.web3.eth.contract(address=contractAddress, abi=et.readAbi("sensor.json"))
        addHeater(Heater(contracth, macAddress, index, connectToSensor(macAddress, index + 1)))
        print("Serial port with sensor " + macAddress + " opened!")

def connectToSensor(macAddress, index):
    rfcommString = '/dev/rfcomm' + str(index)
    Popen(['sudo', 'rfcomm', 'connect', rfcommString, macAddress, '1', '&'])
    sleep(4)
    return serial.Serial(rfcommString, baudrate=9600)

def  sendStatus(port, status):
    print("Sending new status "+ str(status))
    if(status):
        port.write(b'ON')
    else:
        port.write(b'OFF')

def disconnectSensor(rfcommString):
    Popen(['sudo', 'rfcomm', 'release', rfcommString])

def lookUpNearbyBluetoothDevices():
  nearby_devices = bluetooth.discover_devices()
  response = ""
  if(len(nearby_devices) == 0):
      response = "nodevice"
      print('No device found')
  for device_addr in nearby_devices:
      if('Heater' in str(bluetooth.lookup_name(device_addr))):
          print (str(bluetooth.lookup_name(device_addr)) + " [" + str(device_addr) + "]")
          response = response + str(bluetooth.lookup_name(device_addr)) + "&" + str(device_addr) + "#"
  return response

def readySensors(sock):
    sendMessageTo(sock, "ready")
    initEvents()
 
def enabled_heater_callback(event):
    if(event['args']['_enavledId'] == int('128562386')):
        for heater in heaters:
            if(heater.contract.address == event['address']):
                sleep(2)
                print("Activation " + heater.contract.address + " => " + str(et.activationsCall(heaters.contract, int('128562386'))))
                if(et.activationsCall(heater.contract ,int('128562386'))):
                    newStatus = et.heatCall(heater.contract)
                    #ON/OFF ARDUINO
                    semtStatus(heater.port, newStatus)
                    et.communicateStatus(heater.contract, int(newStatus))
                    print("Heater " + str(heater.id) + " : " + heater.contract.address + " communicated his status => " + str(newStatus))

def initEvents():
    for heater in heaters:
        heaters_enabled_filter.append(heater.contract.events.enabled.createFilter(fromBlock='latest'))
        
    while True:
        for enable_filter in heaters_enabled_filter:
            for event in enable_filter.get_new_entries():
                enabled_heater_callback(event)
        sleep(0.5)


receiveMessages()

def demoMode():
    contractAddress0 = '0x2af54A206D2EaEa4ADDC5eE6489DfB3bdf072Cc5'
    contractAddress1 = '0xc7e08392aE35CD9903B2915c1C310B115AC3E548'
    contract0 = et.web3.eth.contract(address=contractAddress0, abi=et.readAbi("heater.json"))
    contract1 = et.web3.eth.contract(address=contractAddress1, abi=et.readAbi("heater.json"))
    heaters.append(Heater(contract0, '98:D3:C1:FD:85:30', 0, connectToSensor('98:D3:C1:FD:85:30', 1)))
    heaters.append(Heater(contract1, '98:D3:11:FC:5D:34', 1, connectToSensor('98:D3:11:FC:5D:34', 2)))
    initEvents()

#demoMode()