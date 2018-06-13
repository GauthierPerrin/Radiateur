import requests
import time
import paho.mqtt.client as mqtt
import json

api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q=Paris'
#city = input ("City name :")
url = api_address #+ city
time.sleep(5)
def on_connect_mqtt(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    
       


#print ("Temperature de la ville: %s" % "{0:.2f}".format(format_data) + " degres")
#humidity = json_data['main']['humidity']
#print ("Taux d'humidité dans l'air: %s" % humidity +" %")
#description = json_data['weather'][0]['description']
#print ("Description: %s" %description)


client = mqtt.Client()
client.on_connect = on_connect_mqtt
client.connect("192.168.0.44", 1883, 60)
#client.connect("192.168.43.175", 1883, 60)


client.loop_start()
while (True):
    json_data = requests.get(url).json()
    format_data =(json_data['main']['temp'])-273
    meteo = ("{0:.2f}".format(format_data))
    print ("Temperature = " + meteo + "°C")
    
    humidity = json_data['main']['humidity']
    print ("Humidité : %s" % humidity +" %")
    
    MQTT_MSG=json.dumps({"meteolocal_temp": meteo})
    client.publish("meteolocal/meteo",MQTT_MSG)
    time.sleep(10)

#Temperature is given in Kelvinis, formula is c =k-273

