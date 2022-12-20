import pandas as pd
import paho.mqtt.client as mqtt
import os
import csv
import threading
from pymongo import MongoClient

task = [pd.DataFrame()]*3
task_type=["dw","df","dh"]
speed=10

def publish(WP):
    wps=WP.to_json(orient='records')
    client_MQTT.publish("WP seq", wps)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe([("Task_add", 0),("Task_del", 0)])

def on_message(client, userdata, msg):
    print(msg.payload.decode('utf-8'))
    topic=msg.topic
    df = pd.read_json(msg.payload.decode('utf-8'),orient='records')
    print(df)
    collection_drone=mydb.WPS
    for i in range(3):
        print(task[i])
    if topic == "Task_add":
        task[0]=pd.concat([task[0],df.loc[df['event'] == "win"]])  
        task[1]=pd.concat([task[1],df.loc[df['event'] == "fire"]]) 
        task[2]=pd.concat([task[2],df.loc[df['event'] == "hum"]]) 
    if topic == "Task_del":
        id=df["id"][0]
        if df["event"][0] == "win":
           task[0]=task[0].loc[task[0]["id"]!=id]
        elif df["event"][0] == "fire":
           task[1]=task[1].loc[task[1]["id"]!=id]
        elif df["event"][0] == "hum":
           task[2]=task[2].loc[task[2]["id"]!=id]
    with open('output_WPS.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        for i in range(3):
            for data in task[i].itertuples():
                writer.writerow([task_type[i],data.id,1,0.002])
    collection_drone.drop()
    #below will be modified
    os.system('python ICS/Access_2022_WP.py')
    drone_WPS=pd.DataFrame(list(collection_drone.find()))
    t = threading.Thread(target=publish,args=(drone_WPS,))
    t.start()
    # for i in range(max(drone_WPS["Drone"])+1):
    #     dronekit_sim.fly(speed,i)

client = MongoClient("mongodb://140.114.89.210:27017/")
mydb = client["Command"]
collection_tasks=mydb.tasks
collection_drone=mydb.WPS
task[0] = pd.DataFrame(list(collection_tasks.find())).query('event=="win"')
task[1] = pd.DataFrame(list(collection_tasks.find())).query('event=="fire"')
task[2] = pd.DataFrame(list(collection_tasks.find())).query('event=="hum"')
client_MQTT = mqtt.Client()
client_MQTT.on_connect = on_connect
client_MQTT.on_message = on_message
client_MQTT.connect("140.114.89.210", 1883)
client_MQTT.loop_forever()