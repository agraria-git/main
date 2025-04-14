#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import MagneticField
import time
import numpy as np
from ellipse import LsqEllipse
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import json
import datetime


def callback(data):
    print("dato")

    #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.magnetic_field.x)
    dataMag.append([data.magnetic_field.x,data.magnetic_field.y])
    #rospy.loginfo(rospy.get_caller_id() + "I heard %s", len(dataMag))
    print(len(dataMag))



def main():
    print("Inicio")
    rospy.init_node('calibMag', anonymous=True)
    global dataMag
    dataMag = []

    sub = rospy.Subscriber("imu/mag", MagneticField, callback)

    while len(dataMag)<1000:
        time.sleep(0.05)
    print(dataMag)
    print(len(dataMag))
    sub.unregister()


    X1 = [c[0] for c in dataMag]   
    X2 = [c[1] for c in dataMag] 
    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot()
    ax.axis('equal')

    ax.plot(X1, X2, 'ro', zorder=1)
    plt.grid()
    plt.savefig('/home/nvidia/catkin_ws/src/main_agv/src/params/mag/aftercalibImu.png')




if __name__ == '__main__':
    main()
