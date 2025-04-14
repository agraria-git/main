#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped, PointStamped
import time
from agv.msg import waypointarray, waypoint
from actionlib_msgs.msg import GoalStatus

def callback(ruta):
	for i in range(ruta.number):
		if(ruta.route[i].mission == "1"):
			actualmission = ruta.route[i].mission
			print('Misión en',i+1)
			for j in range(i+1):
				point = PointStamped()
				point.header.stamp=rospy.Time.now()
				point.header.frame_id=ruta.header.frame_id
				point.point.x=ruta.route[j].x
				point.point.y=ruta.route[j].y
				point.point.z=0
				tramaPub.publish(point)
				#ruta.route.remove(ruta.route[0])
				#print(ruta)
			MissionManager(actualmission)
		else:
			print('No misión en:',i+1)


def MissionManager(mision):
	#goal_status = GoalStatus()
	#goal_status.goal_id=5
	time.sleep(1)
	while(goal_status.status_list.goal_id!=3):
		time.sleep(0.1)
	if(mision=="1"):
		print("Semáforo")
		#semaforo()
	elif(mision=="2"):
		print("Carga")
		#carga()
	elif(mision=="3"):
		print("Parada")
		#parada()
	while(goal_status.goal_id!=1):
		time.sleep(0.1)
		
			#finished

def Status(data):
	#goal_status = GoalStatusArray()
	goal_status = data

def mission_init():
	global tramaPub
	global trama
	global start_point
	global goal_status

	rospy.init_node('mision_node', anonymous=True)
	rate = rospy.Rate(5)
	

	tramaPub = rospy.Publisher('goals', PointStamped, queue_size = 10)

	rospy.Subscriber("fullroute", waypointarray, callback)
	rospy.Subscriber("move_base/status", GoalStatusArray, Status)

	rospy.loginfo("Nodo misiones iniciado")
	while not rospy.is_shutdown():
		rate.sleep()


if __name__ == '__main__':
	try:
		mission_init()
	except(rospy.ROSException, rospy.ROSInterruptException, rospy.ServiceException) as e:
		rospy.logger("Excepcion en nodo misiones: {}".format(str(e)))
		pass
	except KeyboardInterrupt:
		rospy.logger("Keyboard Interupt")
