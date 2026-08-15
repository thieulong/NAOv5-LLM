# Python 2.7
from naoqi import ALProxy

NAO_IP = "10.150.242.8"
NAO_PORT = 9559

battery = ALProxy("ALBattery", NAO_IP, NAO_PORT)

charge = battery.getBatteryCharge()

print("NAO battery charge: {}%".format(charge))
