import pandas as pd
import paho.mqtt.client as mqtt
import os
import csv
from pymongo import MongoClient
task = [pd.DataFrame()]*3
task_type=["dw","df","dh"]
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
        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ')
            for i in range(3):
                for data in task[i].itertuples():
                    writer.writerow([task_type[i],data.id,1,0.002])
        collection_drone.drop()
        os.system('python Access_2022_WP.py')
        client.publish("drone", "100")

client = MongoClient("mongodb://140.114.89.210:27017/")
mydb = client["Command"]
collection_tasks=mydb.tasks
if len(list(collection_tasks.find())) >=1 :
    task[0] = pd.DataFrame(list(collection_tasks.find())).query('event=="win"')
    task[1] = pd.DataFrame(list(collection_tasks.find())).query('event=="fire"')
    task[2] = pd.DataFrame(list(collection_tasks.find())).query('event=="hum"')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883)
client.loop_forever()