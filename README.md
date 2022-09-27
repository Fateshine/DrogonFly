# DrogonFly
## dronekit.py
This file is used to simulate drone.  
Call fly(waypoint,speed) to start the code.  
the waypoint format sould be array type.  
For exampe [[1,1,1],[2,2,2],[3,3,3]] this have 3 waypoint and each waypoint express with [x,y,z]
TiPs:relative pos for now
## Dashboard.py
this file is to create dashboard and the MongoDB ip will be update after I handle the remote database.  
current collection format is below:  
collection_win {id,x,y,z,win,fire,hum}  for result
collection_tasks {id,x,y,z,event,sig,freq} for task
collection_drone {id,x,y,z}