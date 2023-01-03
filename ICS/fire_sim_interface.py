import zmq
import base64
import numpy as np
import cv2
import pandas as pd
from pymongo import MongoClient
from fire_sim import Sim_fire2
from collections import defaultdict
import random
import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print("Connected with result code ")

def image_pocessing(fig):
    #Todo
    return
def Get_sim(st,et, rseed,a,output,time_slot):  # here a is a window!!!!! 
    lay_num=12
    Sim_fire2(st,et,rseed,a,output,time_slot)  # write the simulation in a file.
    Timeline=pd.read_csv(output,sep='/ ',engine='python')
    Sim=defaultdict(dict)
    Sim_real=defaultdict(dict)
    win=[]
    firs=list(Timeline['f'])
    tmp=[i[1:-1].split(', ') for i in firs]
    all_fire=set()
    for i in tmp:
        try:
            all_fire.update([int(k) for k in i])
        except:
            pass
    hum_floors=set([i//lay_num for i in all_fire]+[i//lay_num +1 for i in all_fire])
    fire_floors=set([i//lay_num for i in all_fire])  
    win_floors=set([i//lay_num for i in all_fire]+[i//lay_num -1 for i in all_fire])  # this layer and the lower layer. 
    #print(f"ss {all_floors}")
    for index,row in Timeline.iterrows():
        #print(row)
        tmp=row['f'][1:-1].split(', ')
        tmps=row['f_s'][1:-1].split(', ')
        #print(f"check  {tmp}")
        if len(tmp)==1 and tmp[0]=='':
            Sim[row['t']]['f']=[]
            Sim_real[row['t']]['f']=[]
            Sim[row['t']]['f_s']=[]
            Sim_real[row['t']]['f_s']=[]
        else:
            fire=[int(tmp[i]) for i in range(len(tmp))]
            fire_state=[int(tmps[i]) for i in range(len(tmp))]
            Sim[row['t']]['f']=fire
            Sim[row['t']]['f_s']=fire_state
            Sim_real[row['t']]['f']=fire
            Sim_real[row['t']]['f_s']=fire_state
        tmp=row['w'][1:-1].split(', ')
        #if len(tmp)>0:
        winn=[int(tmp[i]) for i in range(len(tmp))]
        win=[]
        for i in winn:
            if i//lay_num in win_floors: # 
                win.append(i)
        Sim[row['t']]['w']=win
        Sim_real[row['t']]['w']=win
        #except:
            #Sim[row['t']]['w']=[]
        tmp=row['h'][1:-1].split(', ')
        tmps=row['h_s'][1:-1].split(', ')
        try:
            humm=[int(tmp[i]) for i in range(len(tmp))]
            hum_s=[int(tmps[i]) for i in range(len(tmp))]
            h_s=dict(zip(humm,hum_s))
            hum=[];state=[]
            for i in humm:
                if i//lay_num in hum_floors:
                    hum.append(i)
                    state.append(h_s.get(i))
            Sim[row['t']]['h']=hum 
            Sim[row['t']]['h_s']=state
            Sim_real[row['t']]['h']=hum
            Sim_real[row['t']]['h_s']=state
        except:
            Sim[row['t']]['h']=[]
            Sim[row['t']]['h_s']=[]
            Sim_real[row['t']]['h_s']=[]
            Sim_real[row['t']]['h']=[]     
    return Sim,Sim_real,fire_floors, hum_floors, win_floors
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
    client = MongoClient("mongodb://127.0.0.1:27017/")
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

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5555')
socket.setsockopt(zmq.SUBSCRIBE,b'')

client_MQTT = mqtt.Client()
client_MQTT.on_connect = on_connect
client_MQTT.connect("140.114.89.210", 1883)
client_MQTT.loop_start()

while True:
    try:
        frame = socket.recv()
        print(frame)
        print(time.time())
        img = base64.b64decode(frame)
        npimg = np.frombuffer(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        # cv2.imshow("image", source)
        # cv2.waitKey(0)
        image_pocessing(source)
        update_fire_sim()
        client_MQTT.publish("Event", "100")
    finally:
        pass