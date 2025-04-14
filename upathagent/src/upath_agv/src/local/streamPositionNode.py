#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix
import time

def magic_pos_callback(data):
	global cords
	cords =str(data.latitude) + ';' + str(data.longitude)


def savePosition():
	global cords
	cords = ";"
	pub_mqtt_publish = rospy.Publisher('mqtt_publish', String, queue_size=10)
	rospy.init_node('streamPosition', anonymous=True)
	rate = rospy.Rate(10) # 10hz
	sub_magic_pos = rospy.Subscriber('magic_pos', NavSatFix, magic_pos_callback)
	tini=time.time()
	time.sleep(1)
	rospy.loginfo("Nodo streamPosition iniciado")
	while not rospy.is_shutdown():
		if (time.time()-tini > 1) and cords != ";":
			#rospy.loginfo(cords)
			pub_mqtt_publish.publish("hol;" + cords)
			cords = ";"
			tini=time.time()
		rate.sleep()


if __name__ == '__main__':
	try:
		savePosition()
	except (rospy.ROSException, rospy.ROSInterruptException, rospy.ServiceException) as e :
		rospy.logerr("Excepcion en el nodo streamPosition : {}".format(str(e)))
	except KeyboardInterrupt:
		rospy.logerr("Keyboard Interrupt")
