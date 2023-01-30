import pandas as pd
import zmq
import paho.mqtt.client as mqtt
from Flight_Planner_2023 import Get_sim
from collections import defaultdict
import random
import cv2
import os
import base64
import numpy as np
import csv
import threading
from pymongo import MongoClient

task = [pd.DataFrame()]*3
task_type=["dw","df","dh"]
speed=10

def image_pocessing(fig):
    #Todo
    return

def update_fire_sim():
    floor_num=12
    va=3
    rooms_d=pd.read_csv('../data/rooms.csv',sep=',')
    room_AF=dict(zip(list(rooms_d['r']),(zip(list(rooms_d['w']),list(rooms_d['d'])))))
    all_room=len(room_AF)*floor_num
    ii=0
    time_slot=1
    random.seed(ii)
    a=random.sample(range(all_room),va) #fire source 
    output=f"./result/dash/sim_{ii}.csv"
    Sim,Sim_real,fire_floors,hum_floors,win_floors=Get_sim(0,60,ii,a,output,time_slot)
    client = MongoClient("mongodb://140.114.89.210:27017/")
    # Create database called animals
    mydb = client["Command"]
    # Create Collection (table) called shelterA
    collection = mydb.Simfire
    windows=pd.read_csv('../data/all_win.csv',sep=' ')
    collection.delete_many({})
    for key, item in Sim.items():
        for index, row in windows.iterrows():
                if row["id"]in item['f']:
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Close', 'fire': 'Burn', 'hum': 'None'}
                elif row["id"]in item['h']:
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Close', 'fire': 'None', 'hum': 'Have'}
                elif row["id"]in item['w']:
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Open', 'fire': 'None', 'hum': 'None'}
                else: 
                    record={"time": key, "id":row["id"], "x":row["v_1_x"], "y":row["v_1_y"], 
                          "z":row["v_1_z"], 'win': 'Close', 'fire': 'None', 'hum': 'None'}
                collection.insert_one(record)
    return

def publish(WP):
    wps=WP[["x","y","z"]].to_json(orient='records')
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
    # os.system('python ICS/Access_2022_WP.py')
    drone_WPS=pd.DataFrame(list(collection_drone.find()))
    t = threading.Thread(target=publish,args=(drone_WPS,))
    t.start()
    # for i in range(max(drone_WPS["Drone"])+1):
    #     dronekit_sim.fly(speed,i)
    

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5555')
socket.setsockopt(zmq.SUBSCRIBE,b'')

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
client_MQTT.loop_start()

index=0
while True:
    try:
        frame = socket.recv()
        # print(frame)
        # print(time.time())
        img = base64.b64decode(frame)
        npimg = np.frombuffer(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        cv2.imwrite(f'output{index}.jpg', source)
        index+=1
        # cv2.imshow("image", source)
        # cv2.waitKey(0)
        image_pocessing(source)
        update_fire_sim()
    finally:
        pass