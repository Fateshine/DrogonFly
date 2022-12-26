
"""
Main file meant for execution that will run the program and
make the drones fly around the given waypoints
"""


from tello_class import Tello_drone
from grid import Grid
import time
import pygame
import os
import asyncio
import cv2
import paho.mqtt.client as mqtt
import threading


if __name__ == "__main__":
    # The grid is turned off for now for performance
    # grid
    # grid = Grid(main_drone)
    try:
        # pygame.init()
        # screen = pygame.display.set_mode((900, 600))

        main_drone = Tello_drone(0, -50)
        running = True
        last_cRound=main_drone.cRound
        main_drone.client_MQTT.connect("140.114.89.210", 1883)
        main_drone.client_MQTT.loop_start()

        main_drone.socket.bind('tcp://*:5555')
        
        # main_drone.add_waypoints_json("waypoints.json")        
        # cRound = 0
        # check = main_drone.add_waypoints_database(f"{cRound}")
        # cRound = 1
        # main_drone.add_waypoints_database(f"{cRound}")
        # frame = main_drone.drone.get_frame_read().frame
        # cv2.imshow("Image", frame)
        # cv2.waitKey(15000)
        # cv2.destroyAllWindows()

        # screen = pygame.display.set_mode((900, 600))

        main_drone.takeoff()

        # main_drone.move(True)
        
        t = threading.Thread(target=main_drone.send_current_position)
        t.start()

        while running:
            
            if main_drone.get_current_waypoint() == 0:
                main_drone.hover()
                main_drone.reset_waypoints()
                time.sleep(10)
                if main_drone.cRound==last_cRound: break
                # check = main_drone.add_waypoints_database(f"{cRound}")
                # if check: cRound+=1
            last_cRound=main_drone.cRound
            main_drone.move(True)

            # events = pygame.event.get()
            # for event in events:
            #     if event.type == pygame.QUIT:
            #         main_drone.drone.land()
            #         running = False


            #running = grid.tick()

    finally:
        main_drone.land()



# if __name__ == "__main__":
#     asyncio.run(main())







