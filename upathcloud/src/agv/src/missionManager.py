#!/usr/bin/env python3
import rospy
import time
import actionlib
import requests
import cv2
from datetime import datetime
from std_msgs.msg import Bool, String
from geometry_msgs.msg import Pose, Point, Quaternion, PoseStamped, PointStamped
from agv.msg import waypointarray, waypoint
from actionlib_msgs.msg import GoalStatus, GoalStatusArray
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class MissionManager():

	def __init__(self):

		self._node = rospy.init_node('mission_manager_node', anonymous=True)
		self._rate = rospy.Rate(5)
		rospy.loginfo("Nodo MissionManager iniciado")

		self.array_missions = {	"para": 'stop',
								"espera": 'espera',
								"entrega": 'entrega',
								"sem": 'semaforo',
								"foto": 'foto'}
		self._state = 'stop'
		self.FSM_ruta = ""
		self.FSM_misiones = []
		self.FSM_ruta_i = 0
		self.pendingRoute = False
		self.photo_file = "/home/gmv/Documents/img"
		self.photo_saved = ""
		self.next_way = 0
		self.next = "0"
		self.pub_switcher = rospy.Publisher('/MissionManager/FSM/switch', Bool, queue_size = 1)
		self.sub_switcher = rospy.Subscriber('/MissionManager/FSM/switch', Bool, self.FSM)

		self.pub_rutaWP = rospy.Publisher('goals', PointStamped, queue_size = 10)
		self.pub_Logs = rospy.Publisher('dashboardLogs', String, queue_size = 10)
		self.sub_rutaFull = rospy.Subscriber("fullroute", waypointarray, self.cb_rutaFull)
		self.sub_moveBaseStatus = rospy.Subscriber("/move_base/status", GoalStatusArray, self.cb_moveBaseStatus)
		self.sub_IntelImage = rospy.Subscriber("/camera/color/image_raw", Image, self.cb_IntelImg)

		self.waitingImg = False

		time.sleep(1)

		self.pub_switcher.publish(False)

		rospy.spin()


	def FSM(self, msg):
		if msg.data:
			getattr(self, self._state, lambda: error)()
			if self._state!= 'driving':
				rospy.loginfo("Misión finalizada")
				if self.pendingRoute:
					self.newRoute()
				else:
					rospy.loginfo("Ruta finalizada. Sin tareas pendientes.")
					rospy.loginfo("Esperando nueva ruta")
					self.pub_Logs.publish("[INFO] - MissionManager - Ruta finalizada. Sin tareas pendientes.")
					self.pub_Logs.publish("[INFO] - MissionManager - Esperando nueva ruta.")
		else:
			getattr(self, 'stop', lambda: error)()


	def cb_rutaFull(self, msg):
		index_missions = []
		for i in range(msg.number):
			if(msg.route[i].mission != "null"):
				# actualmission = msg.route[i].mission
				rospy.loginfo('Misión {} en índice {}'.format(msg.route[i].mission, i))
				index_missions.append({'i_ruta': i, 'mission': msg.route[i].mission})
			elif(i==msg.number-1):
				rospy.loginfo('Último punto objetivo añadido sin misión: %d',i)
				index_missions.append({'i_ruta': i, 'mission': "para"})
		self.FSM_ruta = msg
		self.FSM_misiones = index_missions
		self.FSM_ruta_i = 0
		self._state = 'newRoute'
		self.pendingRoute = True
		self.pub_Logs.publish("[INFO] - MissionManager - Nueva ruta recibida: {} puntos GPS y {} misiones.".format(msg.number, len(index_missions)))
		self.next_way = 0
		self.pub_Logs.publish("[INFO] - MissionManager - Navengando al primer waypoint.")
		self.pub_switcher.publish(True)
		

	def cb_moveBaseStatus(self, msg):
		# len_status = data.status_list
		if(len(msg.status_list)>0):
			goal_status = msg.status_list[-1].status
			if self._state == 'driving':
				if goal_status==0 or goal_status==1:
					pass
				elif goal_status==3:
					self._state = self.array_missions[self.FSM_misiones[self.FSM_ruta_i-1]['mission']]
					self.next_way = self.next_way + 1
					# rospy.loginfo(self._state)
					self.next = str(self.next_way)
					#self.pub_Logs.publish("[INFO] - MissionManager - Punto objetivo alcanzado, navegando al waypoint: " + self.next + ".")
					self.pub_switcher.publish(True)
				else:
					self._state = 'stop'
					self.pendingRoute = False
					rospy.logerr("Error en la navegación. GoalStatus = {}".format(goal_status))
					self.pub_Logs.publish("[ERROR] - MissionManager - Punto objetivo no alcanzado. Error en la navegación.")
					self.pub_switcher.publish(True)


	def cb_IntelImg(self,foto):
		if self.waitingImg:
			image = bridge.imgmsg_to_cv2(foto, "bgr8")
			now = datetime.now()
			self.photo_saved = self.photo_file + now.strftime("_%Y%m%d_%H%M%S_%f.jpg")
			cv2.imwrite(self.photo_saved,image)
			rospy.loginfo("Image saved")
			self.pub_Logs.publish("[INFO] - MissionManager - Imagen capturada.")
			self.waitingImg = False
		else:
			pass

	def newRoute(self):
		rospy.loginfo('Envío de path')
		self.pub_Logs.publish("[INFO] - MissionManager - Envío de path para el nuevo punto objetivo.")
		if (self.FSM_ruta_i == 0):
			i_prev = 0
		else:
			i_prev = self.FSM_misiones[self.FSM_ruta_i-1]['i_ruta']+1

		for i in range(i_prev, self.FSM_misiones[self.FSM_ruta_i]['i_ruta']+1):
			point = PointStamped()
			point.header.stamp=rospy.Time.now()
			point.header.frame_id=self.FSM_ruta.header.frame_id
			point.point.x=self.FSM_ruta.route[i].x
			point.point.y=self.FSM_ruta.route[i].y
			point.point.z=0
			self.pub_rutaWP.publish(point)
			#ruta.route.remove(ruta.route[0])
			#print(ruta)
		self.pub_rutaWP.publish(point)
		self._state = 'driving'
		self.pub_switcher.publish(True)
		self.FSM_ruta_i = self.FSM_ruta_i + 1
		if (self.FSM_ruta_i >= len(self.FSM_misiones)):
			self.pendingRoute = False


	def stop(self):
		rospy.loginfo('Parada')
		self.pub_Logs.publish("[INFO] - MissionManager - Realizando misión: Parada y continuar.")


	def entrega(self):
		rospy.loginfo("Navegación en pausa")
#		self.pub_Logs.publish("[INFO] - MissionManager - Navegación en pausa. Entrega de paquete. Esperando a confirmación de recogida.")
		self.pub_Logs.publish("[INFO] - MissionManager - Iniciando misión: Entrega de paquete. Esperando confirmación de recogida.")
		input("Press Enter to continue...\n")
		self.pub_Logs.publish("[INFO] - MissionManager - Misión finalizada: Entrega de paquete.")


	def espera(self):
		rospy.loginfo("Navegación en pausa")
#		self.pub_Logs.publish("[INFO] - MissionManager - Navegación en pausa. Parada de 5 segundos.")
		self.pub_Logs.publish("[INFO] - MissionManager - Iniciando misión: Parada de 5 segundos.")
		time.sleep(5)
		self.pub_Logs.publish("[INFO] - MissionManager - Misión finalizada: Parada de 5 segundos.")


	def driving(self):
		rospy.loginfo('Navegando hasta el goal')
		self.next = str(self.next_way)
		if(self.next_way!=0):
			self.pub_Logs.publish("[INFO] - MissionManager - Punto objetivo alcanzado, navegando al waypoint: " + self.next + ".")
		#self.pub_Logs.publish("[INFO] - MissionManager - Navegando al goal.")


	def semaforo(self):
		url = 'http://3.120.224.119/api/upload/'
		data = {"name": 'filename'}
		self.photo_file = "/home/gmv/Documents/Semaforo/img"
		semaforo_verde = False
		self.pub_Logs.publish("[INFO] - MissionManager - Iniciando misión: Semáforo.")
		while not semaforo_verde:
			self.waitingImg = True
			rospy.loginfo("Esperando semáforo en verde")

			timeout = time.time() + 30
			while self.waitingImg:
				if time.time() > timeout:
					rospy.logerr("No se ha podido tomar la imagen")
					self.pub_Logs.publish("[ERROR] - MissionManager - No se ha podido tomar la imagen. Esperando entrada manual para continuar la navegación.")
					input("Presione Enter para continuar con la navegación cuando el semáforo esté verde...\n")
					break
				time.sleep(0.1)

			if self.waitingImg:
				self.waitingImg = False
				break

			files = {'file': open(self.photo_saved, 'rb')}
			response = requests.post(url, data=data, files=files)
			# current_url = response.text
			rospy.loginfo(response.text)

			n_semaforos = response.split('[')[1][1:-4].split('), (')
			rospy.loginfo("Hay %d semáforos detectados", len(n_semaforos))

			i_max_area = -1
			area_max = 0.0
			result = -1
			for j in range(len(n_semaforos)):
				semaforo_i = [eval(k) for k in n_semaforos[j].split(', ')]
				if(semaforo_i[4] != 0 and semaforo_i[5]>0.5):
					if(semaforo_i[2]*semaforo_i[3]>area_max):
						area_max = semaforo_i[2]*semaforo_i[3]
						i_max_area = j
						result = semaforo_i[4]

			if i_max_area>=0:
				if result == 2:
					rospy.loginfo("RED LIGHT")
					rospy.loginfo("Detectado semáforo correspondiente al mensaje: %d", Selected+1)
					self.pub_Logs.publish("[INFO] - MissionManager - Semáforo en rojo. Continúo la espera.")
				elif result == 1:
					rospy.loginfo("GREEN LIGHT")
					rospy.loginfo("Detectado semáforo correspondiente al mensaje: %d", Selected+1)
					#self.pub_Logs.publish("[INFO] - MissionManager - Semáforo en verde. Continúo la navegación.")
					self.pub_Logs.publish("[INFO] - MissionManager - Misión finalizada: Semáforo en verde.")
					semaforo_verde = True
				elif result == 0:
					rospy.loginfo("NO COLOR TRAFFIC LIGHT")
					rospy.loginfo("Detectado semáforo correspondiente al mensaje: %d", Selected+1)
					self.pub_Logs.publish("[INFO] - MissionManager - Semáforo sin color detectado. Continúo la espera.")
				else:
					rospy.loginfo("ERROR DE DETECCIÓN")
					self.pub_Logs.publish("[INFO] - MissionManager - Error en la detección del estado del semáforo. Continúo la espera.")
			else:
				rospy.loginfo("No se ha encontrado semáforo. ESPERANDO SEMAFORO VERDE")


	def foto(self):
		# input("Press Enter to take a photo...")
		self.photo_file = "/home/gmv/Documents/FotosTomadas/img"
		self.waitingImg = True
		timeout = time.time() + 30
		self.pub_Logs.publish("[INFO] - MissionManager - Iniciando misión: Tomar foto.")
		while self.waitingImg:
			if time.time() > timeout:
				rospy.logerr("No se ha podido tomar la imagen")
				self.pub_Logs.publish("[INFO] - MissionManager - No se ha podido tomar la imagen. Esperando entrada manual para continuar la navegación.")
				input("Presione Enter para continuar con la navegación...\n")
				self.pub_Logs.publish("[INFO] - MissionManager - Misión finalizada: Tomar foto - Error.")
				break
			time.sleep(0.1)
		if self.waitingImg:
			self.waitingImg = False
		else:
			self.pub_Logs.publish("[INFO] - MissionManager - Misión finalizada: Foto guardada en " + self.photo_saved + " .")
			#self.pub_Logs.publish("[INFO] - MissionManager - Foto capturada guardada en " + self.photo_saved + " .")
			rospy.loginfo("Foto guardada en " + self.photo_saved)


if __name__ == '__main__':
	try:
		mm = MissionManager()
	except(rospy.ROSException, rospy.ROSInterruptException, rospy.ServiceException) as e:
		rospy.logerr("Excepcion en nodo misiones: {}".format(str(e)))
		self.pub_Logs.publish("[ERROR] - MissionManager - Excepción en nodo MissionManager: {}.".format(str(e)))
	except KeyboardInterrupt:
		rospy.logerr("Keyboard Interupt")
		self.pub_Logs.publish("[INFO] - MissionManager - Interrupción de teclado en nodo MissionManager.")
