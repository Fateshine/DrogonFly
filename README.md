# DrogonFly
## Flight_planner.py
When the task of the dashboard is changed, it will receive the MQTT message, and automatically call the code to calculate the trajectory and then publish the MQTT message to the UAV after completion.
## tello_class.py
The tello class with MQTT and ZMQ(image)
## fly_drone.py
start the drone (In the future, the interface will be added so that pressing the command on the dashboard will automatically start the drone)
## fire_sim_interface.py
Interface of Data Analyzer
## dronekit_sim.py
This file is used to simulate drone.  
currently not used
## Dashboard.py
This file is to create dashboard.  
current collection format is below:  
collection_win {id,x,y,z,win(Open/Close),fire(Burn/None),hum(Have/None),accuracy,detection_time}  for result  
collection_tasks {id,x,y,z,event,sig,freq} for task  
collection_status {Drone(number),x,y,z} for current drone location
collection_drone {Drone(number),x,y,z} for WPS
collection_sim {time,id,x,y,z,win(Open/Close),fire(Burn/None),hum(Have/None),accuracy,detection_time} for simulation

***If you want to run MQTT Broker on your own server, please insatll Mosquitto https://mosquitto.org/ on your server,and assign server IP and port(1883 by default) to the Dashboard.py & MQTT_ICS.py code like this :(client_MQTT.connect("server IP", 1883))***

***dronekit_sim need to run in the enviroment above(environment.yml)***

***I only changed the above file, the others are the same as https://github.com/Fangqierin/Drone_SRDS***
