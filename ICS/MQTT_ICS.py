import pandas as pd
import paho.mqtt.client as mqtt
import os
import csv
import dronekit_sim
from pymongo import MongoClient
task = [pd.DataFrame()]*3
task_type=["dw","df","dh"]
speed=10
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("task", 0)

def on_message(client, userdata, msg):
    print(msg.payload.decode('utf-8'))
    topic=msg.topic
    msg=msg.payload.decode('utf-8').split(",")
    collection_drone=mydb.WPS
    if topic == "task":
        task[0] = pd.DataFrame(list(collection_tasks.find())).query('event=="win"')
        task[1] = pd.DataFrame(list(collection_tasks.find())).query('event=="fire"')
        task[2] = pd.DataFrame(list(collection_tasks.find())).query('event=="hum"')
        with open('output_WPS.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ')
            for i in range(3):
                for data in task[i].itertuples():
                    writer.writerow([task_type[i],data.id,1,0.002])
        collection_drone.drop()
        collection_sim.drop()
        os.system('python Access_2022_WP.py')
        client_MQTT = mqtt.Client()
        client_MQTT.on_connect = on_connect
        client_MQTT.on_message = on_message
        client_MQTT.connect("140.114.89.210", 1883)
        client_MQTT.publish("drone", "100")
        client_MQTT.disconnect()
        drone_WPS=pd.DataFrame(list(collection_drone.find()))
        for i in range(max(drone_WPS["Drone"])+1):
            dronekit_sim.fly(speed,i)

client = MongoClient("mongodb://140.114.89.210:27017/")
mydb = client["Command"]
collection_tasks=mydb.tasks
collection_drone=mydb.WPS
collection_sim=mydb.sim
client_MQTT = mqtt.Client()
client_MQTT.on_connect = on_connect
client_MQTT.on_message = on_message
client_MQTT.connect("140.114.89.210", 1883)
client_MQTT.loop_forever()