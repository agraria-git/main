#!/usr/bin/env python
import telnetlib
import rospy
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import String
import socket
import time
# from std_msgs.msg import Float64
# import time

# def prueba():
	# return [time.time(),0]

# IP = '192.168.224.24'
IP = '192.168.100.24'
# IP = '192.168.60.24'

def lee_tcp_telnet():
	tn= telnetlib.Telnet(IP,9500)
	data = tn.read_until(b"\n")
	data=data.decode("utf-8")
	data = data.split(',')
	# sat= data[22:25]
	sat= data[23:26]
	data = data[2:6]
	lat = float(data[0][0:2]) + float(data[0][2:])/60.0
	if data[3] == 'W':
		lon = -1.0 * float(data[2][0:3]) - float(data[2][3:])/60.0
	else:
		lon = float(data[2][0:3]) + float(data[2][3:])/60.0
	return [lat,lon,sat[0],sat[2]]

def compruebaPuerto():
	global rate
	a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	a_socket.settimeout(2)
	location = (IP,9500)
	result_of_check = a_socket.connect_ex(location)
	if result_of_check == 0:
		rospy.loginfo("Puerto abierto")
		a_socket.close()
		return 1
	else:
		rospy.loginfo("Puerto no abierto")
		return 0


def telnet_talker():
	pub = rospy.Publisher('magic_pos', NavSatFix, queue_size=1)
	# pub = rospy.Publisher('magic_pos', Float64, queue_size=10)
	satPub = rospy.Publisher('satelites', String, queue_size=1)
	rospy.init_node('telnet_talker', anonymous=True)
	global rate
	rate = rospy.Rate(10)
	print("Nodo telnet_ros iniciado")
	while not rospy.is_shutdown() and compruebaPuerto() == 0:
		rate.sleep()
	while not rospy.is_shutdown():
            send_msg = NavSatFix()
            coords = lee_tcp_telnet()
            if(coords[0] == 0 or coords[1] == 0): # or float(coords[2])<2 or float(coords[3])<2):
                pass
            else:
                send_msg.header.stamp = rospy.Time.now()
                send_msg.header.frame_id = "magic"
                send_msg.longitude = coords[1]
                send_msg.latitude = coords[0]
                send_msg.position_covariance = [1e-6,0,0,0,1e-6,0,0,0,1e-6]
                send_msg.position_covariance_type = 1
                satMsg = "Satelites: " + str(coords[2]) + " / " + str(coords[3]) + "    lat: " +str(coords[0])+ " lon: "+str(coords[1])
                satPub.publish(satMsg)
                if (float(coords[2])>=2 and float(coords[3])>=2):
                	pub.publish(send_msg)
                rate.sleep()

if __name__ == '__main__':
	try:
		telnet_talker()
	except rospy.ROSInterruptException:
		tn.close()




