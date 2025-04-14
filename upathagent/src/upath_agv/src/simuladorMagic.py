#!/usr/bin/env python
# from os import posix_fallocate
import telnetlib
import rospy
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import String

from random import randint

# from std_msgs.msg import Float64
import time
t0 = time.time()

# def prueba():
	# return [time.time(),0]

global index 
index = 0
def lee_tcp_telnet():
	global t0
	global index
	t = time.time()
	pos=[[-6.0058469585448675,37.404672940098905,1,1], [-6.005586784264226,37.404623402396986,1,1], [-6.005547221680313,37.40474857824724,1,1] ,[-6.005812760379113,37.40479705054158,1,1]]


	
	post=pos[index]

	#index=index+1
	if(index==3):
			index=0
	return post
	
		



def telnet_talker():
	global t0
	pub = rospy.Publisher('magic_pos', NavSatFix, queue_size=1)
	# pub = rospy.Publisher('magic_pos', Float64, queue_size=10)
	satPub = rospy.Publisher('satelites', String, queue_size=1)
	rospy.init_node('telnet_talker', anonymous=True)
	rate = rospy.Rate(5)
	print("Nodo telnet_ros iniciado")
	while not rospy.is_shutdown():
            send_msg = NavSatFix()
            coords = lee_tcp_telnet()
            send_msg.header.stamp = rospy.Time.now()
            send_msg.header.frame_id = "magic"
            send_msg.longitude = coords[0]
            send_msg.latitude = coords[1]
            satMsg = "Satelites: " + str(coords[2]) + " / " + str(coords[3]) + "    lat: " +str(coords[0])+ " lon: "+str(coords[1])
            satPub.publish(satMsg)
            pub.publish(send_msg)
            rate.sleep()

if __name__ == '__main__':
	try:
		telnet_talker()
	except rospy.ROSInterruptException:
		tn.close()




