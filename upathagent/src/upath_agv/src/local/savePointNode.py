#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix

def magic_pos_callback(data):
	global magic_pose
	magic_pose = data
	# print(data)

def get_coordenadas(data):
	return str(data.latitude) + ';' + str(data.longitude)

def msg_g_callback(data):
	global pub_mqtt_publish
	global magic_pose
	# print("He recibido este mensaje: {}".format(data))
	coords = get_coordenadas(magic_pose)
	msg_answer = data.data + ';' + coords
	pub_mqtt_publish.publish(msg_answer)
	rospy.loginfo("Respuesta a la petición: {}".format(msg_answer))

def guarda_punto():
	global pub_mqtt_publish
	pub_mqtt_publish = rospy.Publisher('mqtt_publish', String, queue_size=10)
	rospy.init_node('guarda_punto_node', anonymous=True)
	rate = rospy.Rate(10) # 10hz
	sub_msg_g = rospy.Subscriber('mqtt_msg_g', String, msg_g_callback)
	sub_magic_pos = rospy.Subscriber('magic_pos', NavSatFix, magic_pos_callback)
	rospy.loginfo("Nodo savePoint iniciado")
	while not rospy.is_shutdown():
		rate.sleep()


if __name__ == '__main__':
	try:
		guarda_punto()
	except (rospy.ROSException, rospy.ROSInterruptException, rospy.ServiceException) as e :
		rospy.logerr("Excepción en el nodo savePoint: {}".format(str(e)))
	except KeyboardInterrupt:
		rospy.logerr("Keyboard Interrupt")
