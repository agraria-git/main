#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
import paho.mqtt.client as mqtt
import json
from geometry_msgs.msg import Pose, Point, Quaternion ,PoseStamped, PointStamped
from main_agv.msg import waypointarray, waypoint
import utm
from math import atan2
from math import pi
import time
from scout_msgs.msg import ScoutStatus

MQTT_HOST = "10.8.0.1"
MQTT_PORT = 8881

MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "/magicppp/robot"
MQTT_LOGS_TOPIC = "/logs"
MQTT_MSG = "hello MQTT"
MQTT_BATTERY = "/battery"

UUID="514a946e"

def mqttMessagePublished(mqttClient, obj, mid):
#Funcion de callback cuando publica algo en el topic MQTT
  rospy.logdebug("mid: "+str(mid))

def mqttSubscribed(mqttClient, obj, mid, granted_qos):
  rospy.loginfo("Subscribed: "+str(mid)+" "+str(granted_qos))

def mqttConnected(mqttClient, obj, flags, rc):
  mqttClient.subscribe(MQTT_TOPIC, 0)

def mqttMessageReceived(mqttClient, obj, msg):
  global pub
  command = json.loads(msg.payload)
  rospy.loginfo("Mensaje recibido del dashboard: {}".format(command))
  if command["command"] == "guardapunto":
    send_str = "1"
    pub.publish(send_str)
  elif command["command"] == "start-reproduce":
    # goalsTransform(str(command["route"]))
    goalsTransform(command['route'])
      

def goalsTransform(data):
  global k
  ruta=waypointarray()
  ruta.header.stamp=rospy.Time.now()
  ruta.header.frame_id="utm"
  for point in data:
    index = data.index(point)
    lat=float(point['lat'])
    lng=float(point['lng'])
    miss=str(point['mision'])
    if index+1 < len(data):
      latProx=data[index+1]['lat']
      lngProx=data[index+1]['lng']
      angle = yaw(lat,lng,latProx,lngProx)
    else:
      latPrev=data[index-1]['lat']
      lngPrev=data[index-1]['lng']
      angle = yaw(latPrev,lngPrev,lat,lng)
    UTMx, UTMy , Z ,N = utm.from_latlon(lat, lng)
    k=k+1
    punto = waypoint()
    punto.stamp=rospy.Time.now()
    punto.frame_id="utm"
    punto.x = UTMx
    punto.y = UTMy
    punto.z = 0
    punto.mission = miss
    ruta.route.append(punto)
    time.sleep(0.1)
  ruta.number = k
  pathPub.publish(ruta) 

def yaw(latOrigen,lonOrigen,latDestino,lonDestino):
        xOrigen,yOrigen,a,b=utm.from_latlon(latOrigen,lonOrigen)
        xDestino,yDestino,a,b=utm.from_latlon(latDestino,lonDestino)
        vxDestino = xDestino - xOrigen
        vyDestino = yDestino - yOrigen
        angle = atan2(vyDestino, vxDestino)
        return angle


def magicCordsCallback(data):
  global mqttClient
  global UUID
  str_in = data.data
  str_in = str_in.split(';')
  coordenadas = [float(str_in[1]),float(str_in[2])]
  coords = {"UUID":UUID,"lat": coordenadas[0],"lng": coordenadas[1]} 
  c = json.dumps(coords) 
  mqttClient.publish("/magicppp", c)



def dashBoard():
  global dashBoardPub
  dashBoardPub = rospy.Publisher('mqtt_cam', String, queue_size=10)

def dashboardLogs_cb(data):
  global mqttClient
  message={"UUID":UUID,"data":data.data}
  c = json.dumps(message) 
  mqttClient.publish(MQTT_LOGS_TOPIC, c)

def battery_cb(data):
  global mqttClient
  global i
  battery_v = data.battery_voltage
  battery_p = (45*battery_v-1045)/2.6
  battery_v = round(battery_v, 2)
  battery_p = round(battery_p, 2)
  bat={"voltage": str(battery_v),"percentage": str(battery_p)} 
  vector_bat = json.dumps(bat)
  if(i>10):
    mqttClient.publish(MQTT_BATTERY, vector_bat)
    i=0
  else:
    i=i+1

def goals():
  global pathPub
  global startSeq

  startSeq = rospy.Publisher('Start_seq' ,String, queue_size = 10)
  pathPub = rospy.Publisher('fullroute', waypointarray, queue_size = 10)

def mqtt_init():
  global mqttClient
  global pub
  global i
  global k
  k = 0
  i = 0
  rospy.init_node('mqtt_ros', anonymous=True)
  rate = rospy.Rate(5) # 10hz

  #Topics de comunicacion con nodoGuardaPunto--------------------------------
  #Envío instrucción al nodo para que me envíe las coordenadas del magic
  pub = rospy.Publisher('mqtt_msg_g', String, queue_size=10)
  #Recibo las coordenadas del magic de guarda punto
  rospy.Subscriber("mqtt_publish", String, magicCordsCallback)

  rospy.Subscriber("dashboardLogs", String, dashboardLogs_cb)

  rospy.Subscriber("/scout_status", ScoutStatus, battery_cb)
  #--------------------------------------------------------------------------

  #Declara el publicador de la camara-----------------------------------------
  dashBoard()
  #--------------------------------------------------------------------------

  #Declara el publicador de goals y startseq---------------------------------
  goals()
  #--------------------------------------------------------------------------

  #Comunicación MQTT con el dashboard----------------------------------------
  mqttClient = mqtt.Client(transport='websockets')   
  mqttClient.on_message = mqttMessageReceived
  mqttClient.on_connect = mqttConnected
  mqttClient.on_publish = mqttMessagePublished
  mqttClient.on_subscribe = mqttSubscribed
  mqttClient.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
  #--------------------------------------------------------------------------

  rospy.loginfo("Nodo mqtt_ros iniciado")
  while not rospy.is_shutdown():
    mqttClient.loop() 
    rate.sleep()
    # time.sleep(0.01)
  

if __name__ == '__main__':
  try:
    mqtt_init()
  except (rospy.ROSException, rospy.ROSInterruptException, rospy.ServiceException) as e :
    rospy.logerr("Excepción en el nodo MQTT: {}".format(str(e)))
    mqttClient.disconnect()
    mqttClient.loop_stop() 
  except KeyboardInterrupt:
    rospy.logerr("Keyboard Interrupt")
    mqttClient.disconnect()
    mqttClient.loop_stop() 
