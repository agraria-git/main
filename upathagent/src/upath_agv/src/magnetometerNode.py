#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import MagneticField
import json
import numpy as np

def callback(data):
    print("callback")
    global seq
    global Hs
    global Rm
    global wscale
    global pub
    sensor = np.array((data.magnetic_field.x,data.magnetic_field.y))
    sensor = sensor - Hs
    sensor = np.dot(Rm,sensor)
    sensor = np.dot(wscale,sensor)
    magnetMessage = MagneticField()
    magnetMessage.header.frame_id = 'imu_link'
    magnetMessage.header.stamp = rospy.Time.now()
    magnetMessage.magnetic_field.x = np.float(sensor[0])
    magnetMessage.magnetic_field.y = np.float(sensor[1])
    magnetMessage.magnetic_field.z = np.float(data.magnetic_field.z)
    magnetMessage.header.seq = seq
    seq = seq + 1
    pub.publish(magnetMessage)


def getparams():
    with open('/home/nvidia/catkin_ws/src/agv/src/params/mag/calibData.json', 'r') as f:
        data = json.load(f)
    return data
    
def listener():
    rospy.init_node('magnetometer', anonymous=True)

    global Rm
    global wscale
    global Hs
    global pub
    global seq
    seq = 0

    pub = rospy.Publisher('imu/mag', MagneticField, queue_size=10)

    params = getparams()
    phi = params["phi"]
    xscale = params["xscale"]
    yscale = params["yscale"]
    Hsx = params["Hsx"]
    Hsy = params["Hsy"]
    theta = -phi
    c, s = np.cos(theta), np.sin(theta)

    Rm = np.array(((c, -s), (s, c)))
    wscale = np.array(([xscale,0],[0,yscale]))
    Hs = np.array((Hsx,Hsy))


    rospy.Subscriber("/imu/mag_raw", MagneticField, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()