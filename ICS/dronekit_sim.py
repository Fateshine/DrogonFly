from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative,Locations,LocationLocal
from pymavlink import mavutil # Needed for command message definitions
import time
import math
import argparse
import pandas as pd  
import dronekit_sitl
from datetime import datetime
from pymongo import MongoClient
# #Set up option parsing to get connection string
# import argparse  
# parser = argparse.ArgumentParser(description='Control Copter and send commands in GUIDED mode ')
# parser.add_argument('--connect', 
#                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
# args = parser.parse_args()

# connection_string = args.connect
# sitl = None

# #Start SITL if no connection string specified
#     if not connection_string:
#         import dronekit_sitl
#         sitl = dronekit_sitl.start_default()
#         connection_string = sitl.connection_string()


# # Connect to the Vehicle
# print('Connecting to vehicle on: %s' % connection_string)
# vehicle = connect(connection_string, wait_ready=True)

def arm_and_takeoff(aTargetAltitude):
        #Set up option parsing to get connection string
        parser = argparse.ArgumentParser(description='Control Copter and send commands in GUIDED mode ')
        parser.add_argument('--connect', 
                        help="Vehicle connection target string. If not specified, SITL automatically started and used.")
        args = parser.parse_args()

        connection_string = args.connect
        global sitl
        sitl = None

        #Start SITL if no connection string specified
        if not connection_string:
            sitl = dronekit_sitl.start_default()
            connection_string = sitl.connection_string()


        # Connect to the Vehicle
        print('Connecting to vehicle on: %s' % connection_string)
        global vehicle 
        vehicle = connect(connection_string, wait_ready=True)

        """
        Arms vehicle and fly to aTargetAltitude.
        """
        
        print("Basic pre-arm checks")
        # Don't let the user try to arm until autopilot is ready
        while not vehicle.is_armable:
            print(" Waiting for vehicle to initialise...")
            time.sleep(1)

            
        print("Arming motors")
        # Copter should arm in GUIDED mode
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True

        while not vehicle.armed:      
            print(" Waiting for arming...")
            time.sleep(1)

        print("Taking off!")
        vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
            if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
                print("Reached target altitude")
                break
            time.sleep(1)
#Arm and take of to altitude of 5 meters



"""
Convenience functions for sending immediate/guided mode commands to control the Copter.

The set of commands demonstrated here include:
* MAV_CMD_CONDITION_YAW - set direction of the front of the Copter (latitude, longitude)
* MAV_CMD_DO_SET_ROI - set direction where the camera gimbal is aimed (latitude, longitude, altitude)
* MAV_CMD_DO_CHANGE_SPEED - set target speed in metres/second.


The full set of available commands are listed here:
http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/
"""

"""
Functions to make it easy to convert between the different frames-of-reference. In particular these
make it easy to navigate in terms of "metres from the current position" when using commands that take 
absolute positions in decimal degrees.

The methods are approximations only, and may be less accurate over longer distances, and when close 
to the Earth's poles.

Specifically, it provides:
* get_location_metres - Get LocationGlobal (decimal degrees) at distance (m) North & East of a given LocationGlobal.
* get_distance_metres - Get the distance between two LocationGlobal objects in metres
* get_bearing - Get the bearing in degrees to a LocationGlobal
"""

def get_location_metres(original_location, dNorth, dEast,Alt):
    """
    Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`. The returned LocationGlobal has the same `alt` value
    as `original_location`.

    The function is useful when you want to move the vehicle around specifying locations relative to 
    the current vehicle position.

    The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.

    For more information see:
    http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
    """
    earth_radius = 6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    newalt = original_location.alt + Alt
    if type(original_location) is LocationGlobal:
        targetlocation=LocationGlobal(newlat, newlon,newalt)
    elif type(original_location) is LocationGlobalRelative:
        targetlocation=LocationGlobalRelative(newlat, newlon,newalt)
    else:
        raise Exception("Invalid Location object passed")
        
    return targetlocation;


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    dalt = aLocation2.alt - aLocation1.alt
    return math.pow(((dlat*dlat) + (dlong*dlong))* 1.113195e5 + (dalt*dalt), 1.0/3 ) 


def get_bearing(aLocation1, aLocation2):
    """
    Returns the bearing between the two LocationGlobal objects passed as parameters.

    This method is an approximation, and may not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """	
    off_x = aLocation2.lon - aLocation1.lon
    off_y = aLocation2.lat - aLocation1.lat
    bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
    if bearing < 0:
        bearing += 360.00
    return bearing;



"""
Functions to move the vehicle to a specified position (as opposed to controlling movement by setting velocity components).

The methods include:
* goto_position_target_global_int - Sets position using SET_POSITION_TARGET_GLOBAL_INT command in 
    MAV_FRAME_GLOBAL_RELATIVE_ALT_INT frame
* goto_position_target_local_ned - Sets position using SET_POSITION_TARGET_LOCAL_NED command in 
    MAV_FRAME_BODY_NED frame
* goto - A convenience function that can use Vehicle.simple_goto (default) or 
    goto_position_target_global_int to travel to a specific position in metres 
    North and East from the current location. 
    This method reports distance to the destination.
"""

def goto_position_target_global_int(aLocation):
    """
    Send SET_POSITION_TARGET_GLOBAL_INT command to request the vehicle fly to a specified LocationGlobal.

    For more information see: https://pixhawk.ethz.ch/mavlink/#SET_POSITION_TARGET_GLOBAL_INT

    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.
    """
    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame
        0b0000111111111000, # type_mask (only speeds enabled)
        aLocation.lat*1e7, # lat_int - X Position in WGS84 frame in 1e7 * meters
        aLocation.lon*1e7, # lon_int - Y Position in WGS84 frame in 1e7 * meters
        aLocation.alt, # alt - Altitude in meters in AMSL altitude, not WGS84 if absolute or relative, above terrain if GLOBAL_TERRAIN_ALT_INT
        0, # X velocity in NED frame in m/s
        0, # Y velocity in NED frame in m/s
        0, # Z velocity in NED frame in m/s
        0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    # send command to vehicle
    vehicle.send_mavlink(msg)



def goto_position_target_local_ned(north, east, down):
    """	
    Send SET_POSITION_TARGET_LOCAL_NED command to request the vehicle fly to a specified 
    location in the North, East, Down frame.

    It is important to remember that in this frame, positive altitudes are entered as negative 
    "Down" values. So if down is "10", this will be 10 metres below the home altitude.

    Starting from AC3.3 the method respects the frame setting. Prior to that the frame was
    ignored. For more information see: 
    http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_local_ned

    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.

    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111111000, # type_mask (only positions enabled)
        north, east, down, # x, y, z positions (or North, East, Down in the MAV_FRAME_BODY_NED frame
        0, 0, 0, # x, y, z velocity in m/s  (not used)
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 
    # send command to vehicle
    vehicle.send_mavlink(msg)



def goto(dNorth, dEast,dalt,speed,number):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.

    The method takes a function pointer argument with a single `dronekit.lib.LocationGlobal` parameter for 
    the target position. This allows it to be called with different position-setting commands. 
    By default it uses the standard method: dronekit.lib.Vehicle.simple_goto().

    The method reports the distance to target every two seconds.
    """
    
    currentLocation = vehicle.location.global_relative_frame
    targetLocation = get_location_metres(currentLocation, dNorth, dEast,dalt)
    targetDistance = get_distance_metres(currentLocation, targetLocation)
    vehicle.simple_goto(targetLocation,airspeed=speed)
    
    #print "DEBUG: targetLocation: %s" % targetLocation
    #print "DEBUG: targetLocation: %s" % targetDistance
    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        #print "DEBUG: mode: %s" % vehicle.mode.name
        remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, targetLocation)
        print("drone",number)
        print("Distance to target: ", remainingDistance)
        print("Current location: ",vehicle.location.local_frame)
        print("Current Speed: ",vehicle.airspeed)
        print("Current Time " + str( math.floor(time.time()-start)))
        data={'Drone':str(number),'x':vehicle.location.local_frame.east,'y':vehicle.location.local_frame.north,'z':-vehicle.location.local_frame.down,'time':str( math.floor(time.time()-start)),'speed':vehicle.airspeed}
        collection_sim.insert_one(data)
        # f.write("Distance to target: "+ str(remainingDistance))
        # f.write("Current location: "+ str(vehicle.location.global_frame))
        # f.write("Current Speed: "+ str(vehicle.airspeed))
        # f.write("Current Time " + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S %p")))
        if abs(remainingDistance) <= 0.25: #Just below target, in case of undershoot.
            print("Reached target")
            break;
        time.sleep(2)
    
def fly(speed,number):
    client = MongoClient("mongodb://140.114.89.210:27017/")
    mydb = client["Command"]
    global drone_sim,collection_sim,time1,start
    collection_sim=mydb.sim
    collection_drone=mydb.WPS
    drone_WPS = pd.DataFrame(list(collection_drone.find({"Drone":number}))).drop_duplicates(subset=['Drone','x','y','z']).reset_index()
    drone_sim = pd.DataFrame(list(collection_sim.find()))
    arm_and_takeoff(5)
    vehicle.airspeed = speed
    # while vehicle.parameters['SIM_SPEEDUP'] != simspeed:
    #     print("Setting SIM_SPEEDUP")
    #     vehicle.parameters['SIM_SPEEDUP'] = simspeed
    #     time.sleep(0.1)
    print(drone_WPS)
    point_last=[0,0,5]
    start = time.time()
    for i,point in enumerate(drone_WPS.itertuples()):
        if i==0:
            continue
        goto(point.y-point_last[0], point.x-point_last[1], point.z-point_last[2],speed,number)
        point_last=[point.y,point.x,point.z]
    print("Setting LAND mode...")
    vehicle.mode = VehicleMode("LAND")

    #Close vehicle object before exiting script 
    print("Close vehicle object")
    vehicle.close()
    # Shut down simulator if it was started.
    if sitl is not None:
        sitl.stop()

    print("Completed")
    return
# for i in range(3):
#         fly(10,i)
# waypoint=[[50,50,10],[20,20,10]]
# fly(waypoint,10)
# path = 'output.txt'
# start = time.time()
# with open(path, 'w') as f:
#     f.write('123')
#     fly(waypoint,10,2)
# end = time.time()
# print("執行時間：%f 秒" % (end - start))
