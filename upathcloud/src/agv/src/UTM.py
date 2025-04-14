#!/usr/bin/env python3

from codecs import latin_1_decode
import rospy
from std_msgs.msg import String
import paho.mqtt.client as mqtt
import json
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Pose, Point, Quaternion ,PoseStamped, PointStamped
from nav_msgs.msg import Odometry
import utm
import tf


def cb_odom(data):
    global cordsUTM, tf_listener
    try:
        (trans,rot) = tf_listener.lookupTransform('/utm', '/base_link', rospy.Time(0))
        bl_pose=PoseStamped()
        bl_pose.header.stamp = rospy.Time.now()
        bl_pose.header.frame_id = "utm"
        bl_pose.pose.position.x = trans[0]
        bl_pose.pose.position.y = trans[1]
        bl_pose.pose.position.z = 0
        bl_pose.pose.orientation.x = rot[0]
        bl_pose.pose.orientation.y = rot[1]
        bl_pose.pose.orientation.z = rot[2]
        bl_pose.pose.orientation.w = rot[3]
        cordsUTM.publish(bl_pose)

    except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        pass

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
    global cordsUTM, tf_listener
    rospy.init_node('utmNode', anonymous=True)
    rate = rospy.Rate(5) # 10hz
    # cordsUTM = rospy.Publisher('utm_cords' ,PointStamped, queue_size = 10)
    # sub_magic_pos = rospy.Subscriber('magic_pos', NavSatFix,magic)
    tf_listener = tf.TransformListener()
    cordsUTM = rospy.Publisher('base_link_utm' ,PoseStamped, queue_size = 10)
    sub_baseLink_pos = rospy.Subscriber('odom', Odometry, cb_odom)
    rospy.loginfo("Nodo UTM iniciado")
    while not rospy.is_shutdown():
        rate.sleep()



if __name__ == '__main__':
    try:
        UTM()
    except (rospy.ROSException, rospy.ROSInterruptException, rospy.ServiceException) as e :
        rospy.logerr("Excepción en el nodo UTM: {}".format(str(e)))
        pass
    except KeyboardInterrupt:
        rospy.logerr("Keyboard Interrupt")