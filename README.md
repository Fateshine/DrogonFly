# DrogonFly
## MQTT_ICS.py
When the task of the dashboard is changed, it will receive the MQTT message, and automatically call the code to calculate the trajectory and simulation, and then publish the MQTT message to the dashboard after completion.
## dronekit.py
This file is used to simulate drone.  
Will be called automatically by MQTT_ICS.py when a task is modified in the dashboard   
## Dashboard.py
this file is to create dashboard and the MongoDB ip will be update after I handle the remote database.  
current collection format is below:  
collection_win {id,x,y,z,win,fire,hum,accuracy,detection_time}  for result  
collection_tasks {id,x,y,z,event,sig,freq} for task  
collection_drone {id,x,y,z}

***Please insatll MQTT broker(Mosquitto) https://mosquitto.org/ on ICS server,and assign server IP and port(1883 by default) to the Dashboard.py & MQTT_ICS.py code  like this :(client_MQTT.connect("server IP", 1883))***



