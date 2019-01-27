# Auteur    : Patrick Pinard
# Date      : 27.12.2018
# Objet     : interface mqtt avec Cayenne My devices sur Yoctopuce Wifi comprenant un relai 5 ports, une sonde twmpérature et un display
#             proxy au travers du Raspberry PI avec le code ci-dessous.
# Version   : 1
# Statut    : ok, fonctionnel
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import time
from yoctopuce.yocto_api import *
from yoctopuce.yocto_humidity import *
from yoctopuce.yocto_temperature import *
from yoctopuce.yocto_pressure import *
from yoctopuce.yocto_relay import *
from yoctopuce.yocto_lightsensor import *
from yoctopuce.yocto_display import *

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard. 
MQTT_USERNAME           = "your Cayenne username" 
MQTT_PASSWORD           = "your Cayenne password" 
MQTT_CLIENT_ID          = "your Cayenne ID" 
MQTT_SERVER             = "mqtt.mydevices.com"
MQTT_SECURE_PORT        = 8883          #secure mqtt port
MQTT_PORT               = 1883          #standard mqtt port number
YOCTO_IP_ADDRESS        = "IP address of the Yoctopuce hub"
TIME_TO_SLEEP           = 3600000       #(1000 * 60 * 60 = 1hr)

# Cayenne widget information according to the Dashboard.
ID                  = 'v1/'+ MQTT_USERNAME + '/things/' + MQTT_CLIENT_ID 
relay1_cmd_widget   = ID + '/cmd/2'     # relay 1 -> receive Actuator command
relay1_data_widget  = ID + '/data/2'    # relay 1 -> send Actuator Updated Value
relay2_cmd_widget   = ID + '/cmd/7'     # relay 2 -> receive Actuator command
relay2_data_widget  = ID + '/data/7'    # relay 2 -> send Actuator Updated Value
relay3_cmd_widget   = ID + '/cmd/9'     # relay 3 -> receive Actuator command
relay3_data_widget  = ID + '/data/9'    # relay 3 -> send Actuator Updated Value
relay4_cmd_widget   = ID + '/cmd/10'    # relay 4 -> receive Actuator command
relay4_data_widget  = ID + '/data/10'   # relay 4 -> send Actuator Updated Value
light_widget        = ID + '/data/8'    # light display
temperature_widget  = ID + '/data/1'    # temperature Gauge
humidity_widget     = ID + '/data/3'    # humidity graph
pressure_widget     = ID + '/data/4'    # pressure Gauge

##############################
#  Yoctopuce initialisation  #
##############################

print(" ")
print("---------------------------------------")
print("      WELCOME ON IoT 4 Dummies         ")
print(" Yoctopuce and Raspberry Pi IoT testing")
print("      Patrick Pinard, Décembre 2018    ")
print("")


def die(msg):
    sys.exit(msg + ' (Check IP or USB cable !)')

errmsg = YRefParam()

# Setup the API to use local Yoctopuce Wireless Hub

if YAPI.RegisterHub(YOCTO_IP_ADDRESS, errmsg) != YAPI.SUCCESS:
    sys.exit("... Yoctopuce HUB init error...." + errmsg.value)

# setup Yoctopuce meteo sensor module

sensor = YHumidity.FirstHumidity()
if sensor is None:
    die('No module METEO (T,H,P) connected')
m = sensor.get_module()
target_sensor = m.get_serialNumber()


# setup Yoctopuce relay sensor module

relay_module = YRelay.FirstRelay()
if relay_module is None:
        die('No module RELAY connected')
n = relay_module.get_module()
target_relay = n.get_serialNumber()

# setup Yoctopuce DISPLAY  module

disp = YDisplay.FirstDisplay()
if disp is None:
    die('No module DISPLAY connected')
d = disp.get_module()
target_display = d.get_serialNumber()

# display clean up
disp.resetAll()

# retreive the display size
w = disp.get_displayWidth()
h = disp.get_displayHeight()

# retreive the first layer
l0 = disp.get_displayLayer(0)
l0.clear()

# display a text in the middle of the screen
l0.drawText(w / 2, h / 2, YDisplayLayer.ALIGN.CENTER, "IoT 4 Dummies !")
YAPI.Sleep(1000)

# Display Yoctopuce modules information
print("---------------------------------------")
print(" Yoctopuce module 1 = " + target_sensor)
print(" Yoctopuce module 2 = " + target_relay)
print(" Yoctopuce module 3 = " + target_display)
print("---------------------------------------")
print(" Set all relay to default mode : OFF")
print(" Mesure are done every : " + str(TIME_TO_SLEEP/1000/60) + " mn")
print("---------------------------------------")
print("  Go on Cayenne my devices web site    ")
print("    http://cayenne.mydevices.com       ")
print(" to manage the devices from everywhere ")
print("---------------------------------------")

# Find Relay on Yoctopuce Wifi Hub Relay module (target_relay)
relay1 = YRelay.FindRelay(target_relay + '.relay' + '1')
relay2 = YRelay.FindRelay(target_relay + '.relay' + '2')
relay3 = YRelay.FindRelay(target_relay + '.relay' + '3')
relay4 = YRelay.FindRelay(target_relay + '.relay' + '4')

# Set all Relay to default mode : OFF
relay1.set_output(YRelay.OUTPUT_OFF)
relay2.set_output(YRelay.OUTPUT_OFF)
relay3.set_output(YRelay.OUTPUT_OFF)
relay4.set_output(YRelay.OUTPUT_OFF)

####################
# MQTT / Cayenne   #
####################

# The callback for message is received from Cayenne. 

def on_message(client,userdata, msg):
    m = msg.topic.split('/')                
    p = msg.payload.decode().split(',')     
    module = m[5]
    if module=='2':
        client.publish(relay1_data_widget, p[1])
        if p[1]=='1':
            relay1.set_output(YRelay.OUTPUT_ON)
            #print("Relai 1 is ON")
        else:
            relay1.set_output(YRelay.OUTPUT_OFF)
            #print("Relai 1 is OFF")
    if module=='7':
        client.publish(relay2_data_widget, p[1])
        if p[1]=='1':
            relay2.set_output(YRelay.OUTPUT_ON)
            #print("Relai 2 is ON")
        else:
            relay2.set_output(YRelay.OUTPUT_OFF)
            #print("Relai 2 is OFF")
    if module=='9':
        client.publish(relay3_data_widget, p[1])
        if p[1]=='1':
            relay3.set_output(YRelay.OUTPUT_ON)
            #print("Relai 3 is ON")
        else:
            relay3.set_output(YRelay.OUTPUT_OFF)
            #print("Relai 3 is OFF")
    if module=='10':
        client.publish(relay4_data_widget, p[1])
        if p[1]=='1':
            relay4.set_output(YRelay.OUTPUT_ON)
            #print("Relai 4 is ON")
        else:
            relay4.set_output(YRelay.OUTPUT_OFF)
            #print("Relai 4 is OFF")

# MQTT connexion to Cayenne Cloud Services. 

client = mqtt.Client(MQTT_CLIENT_ID)
client.username_pw_set(MQTT_USERNAME,MQTT_PASSWORD)
client.connect(MQTT_SERVER,MQTT_PORT)
client.on_message = on_message
client.subscribe(relay1_cmd_widget)
client.subscribe(relay2_cmd_widget)
client.subscribe(relay3_cmd_widget)
client.subscribe(relay4_cmd_widget)
client.loop_start()

# Loop to read temp, hum and pressure values and refresh display. 

# display clean up
disp.resetAll()

while m.isOnline():
   
    curr_time = time.strftime(" %d %b %Y à %H:%M:%S")
    humSensor = YHumidity.FindHumidity(target_sensor + '.humidity')
    pressSensor = YPressure.FindPressure(target_sensor + '.pressure')
    tempSensor = YTemperature.FindTemperature(target_sensor + '.temperature')

    t = tempSensor.get_currentValue()
    h = humSensor.get_currentValue()
    p = pressSensor.get_currentValue()
 

    l0.drawText(10, 10, YDisplayLayer.ALIGN.CENTER_LEFT, "Température__(  °C ) = " )
    l0.drawText(10, 20, YDisplayLayer.ALIGN.CENTER_LEFT, "Humidité______(  %  ) = " )
    l0.drawText(10, 30, YDisplayLayer.ALIGN.CENTER_LEFT, "Pression_____( hPa ) = ")
    l0.drawText(60, 50, YDisplayLayer.ALIGN.CENTER, "Dernière mesure : ")

    client.publish(temperature_widget,str(t))
    client.publish(pressure_widget,str(p))
    client.publish(humidity_widget,str(h)
    
    l1 = disp.get_displayLayer(1)
    l1.clear()
    l1.drawText(110, 10, l1.ALIGN.CENTER_RIGHT, str(t))
    l1.drawText(110, 20, l1.ALIGN.CENTER_RIGHT, str(h))
    l1.drawText(110, 30, l1.ALIGN.CENTER_RIGHT, str(p))
    l1.drawText(60, 60, l1.ALIGN.CENTER, str(curr_time))


    YAPI.Sleep(TIME_TO_SLEEP)

YAPI.FreeAPI()
   


