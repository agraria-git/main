#!/usr/bin/env python3

from codecs import latin_1_decode
import rospy
from std_msgs.msg import String
import paho.mqtt.client as mqtt
import json
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Pose, Point, Quaternion ,PoseStamped, PointStamped
import utm


def magic(data):
    global cordsUTM
    lat=data.latitude
    lon=data.longitude
    UTMx, UTMy , Z ,N = utm.from_latlon(lat, lon)
    point=PointStamped()
    point.header.stamp=rospy.Time.now()
    point.header.frame_id="utm"
    point.point.x=UTMx
    point.point.y=UTMy
    point.point.z=0
    cordsUTM.publish(point)

def UTM():
    global cordsUTM
    rospy.init_node('utmNode', anonymous=True)
    rate = rospy.Rate(5) # 10hz
    cordsUTM = rospy.Publisher('utm_cords' ,PointStamped, queue_size = 10)
    sub_magic_pos = rospy.Subscriber('magic_pos', NavSatFix,magic)
    while not rospy.is_shutdown():
        rate.sleep()



if __name__ == '__main__':
  try:
    UTM()
  except KeyboardInterrupt:
    pass
