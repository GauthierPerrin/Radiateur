
#!/usr/bin/python2.7
import paho.mqtt.client as mqtt
import json
from decimal import Decimal
import time
import pymysql
import datetime
import requests

api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q=Paris'
url = api_address
json_data = requests.get(url).json()
temperature  =(json_data['main']['temp'])-273
#humidity = json_data['main']['humidity']


tempRad = float (28)
tempSall = float (20)
consigne = float (24)
tempExt = float ("{0:.2f}".format(temperature))
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='pi', db='ProjetBTS')
#Heure = datetime.datetime.now()
# The callback for when the client receives a CONNACK response from the server.
def on_connect_mqtt(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("meteolocal/#")
    client.subscribe("/esp1/temperature/#")
    client.subscribe("/esp1/humidity/#")
    client.subscribe("/esp2/temperature/#")
    client.subscribe("/esp2/humidity/#")
    client.subscribe("/esp3/temperature/#")
    client.subscribe("/esp3/humidity/#")

# The callback for when a PUBLISH message is received from the server.
# commande de publication :
# Linux mosquitto_pub -h 192.168.0.44 -t sensor/temperature -m '{"sensor_id":"radiateur","temp":"13.23"}'
# Windows : mosquitto_pub -h 192.168.0.44 -t sensor/temperature -m {\"sensor_id\":\"radiateur\",\"temp\":\"13.56\"}
  
    
def enregistrement (Piece,Radiateur,Exterieur,Consigne,Moyenne):
    global conn
    Heure = datetime.datetime.now()
    ligne = []
    ligne.append((Heure,Piece,Radiateur,Exterieur,Consigne,Moyenne))
    cursor = conn.cursor()
    cursor.executemany("""INSERT INTO temperatures(Heure, Temp_salle, Temp_radiateur, Temp_exterieur,Consigne, Moyenne) VALUES(%s, %s, %s, %s, %s, %s)""", ligne)
    conn.commit()

def on_message_mqtt(client, userdata, msg):
    global tempRad
    global consigne
    global tempExt
    global tempSall
    data = json.loads(str(msg.payload),parse_float=Decimal)
    if (msg.topic == "/esp1/temperature" or msg.topic == "/esp1/humidity"):
        #print("esp1 = " + str(data) + "°C")
        #print("esp1 = " + str(data) + "%")
        tempRad = float (data)
    elif (msg.topic == "/esp2/temperature" or msg.topic == "/esp2/humidity"):
        #print("esp2 = " + str(data) + "°C")
        #print("esp2 = " + str(data) + "%")
        consigne  = float (data)
    elif (msg.topic == "/esp3/temperature" or msg.topic == "/esp3/humidity"):
        #print("esp3 = " + str(data) + "°C")
        #print("esp3 = " + str(data) + "%")
        consigne = float(data)
    elif (msg.topic == "meteolocal/meteo"):
        #print ("TmpExt = "+ str (tempExt))
        tempExt = float (data["meteolocal_temp"])

    #enregistrement(consigne,tempRad,tempExt)

    Moyenne =  (consigne + tempRad + tempExt)/3
    deltaTemp = consigne - Moyenne

    enregistrement(consigne,tempRad,tempExt,tempSall,Moyenne)
    #print (Moyenne)
    #print (deltaTemp)
    if (deltaTemp < 0):
        deltaTemp = deltaTemp * (-1)
    if (deltaTemp > 0 and deltaTemp < 2):
        Ventilateur = 0
        Binaire = 0 
    elif (deltaTemp > 2 and deltaTemp < 4):
        Ventilateur = 0
        Binaire = 0 
    elif (deltaTemp > 4 and deltaTemp < 6):
        Ventilateur = 0
        Binaire = 1 
    elif (deltaTemp > 6 and deltaTemp < 8):
        Ventilateur = 0
        Binaire = 1 
    elif (deltaTemp > 8) :
        Ventilateur = 0
        Binaire = 1 


        
    MQTT_MSG=json.dumps (Ventilateur)
    client.publish("/esp3/ventilateur",MQTT_MSG)


    print (Ventilateur)




def create_table ():
    global conn
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS temperatures(
     Heure datetime,
     Temp_salle float,
     Temp_radiateur float,
     Temp_exterieur float,
     Consigne float,
     Moyenne float
     )
     """)
    conn.commit()

create_table()
client = mqtt.Client()
client.on_connect = on_connect_mqtt
client.on_message = on_message_mqtt



#client.connect("192.168.0.44", 1883, 60)
client.connect("192.168.43.175", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
coon.close()
