#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Imu
from sensor_msgs.msg import MagneticField


import serial
import time
import array
import sys
import numpy as np
import math
import struct
import os
from tf.transformations import quaternion_from_euler 
# os.system("sudo chmod 666 /dev/IMU")




os.system("echo 'nvidia' | sudo -S chmod 666 /dev/IMU")

trama=[]
trama_b = []
rx_i = 0
llena = False

seq = 0

ang = 0
vel = 0
acel = 0
mag = 0

degrees2rad = math.pi/180.0

def pintarTrama(trama):
    k = ""
    for i in trama:
        k = k + " " +  str(i)
    print(k)

def calcularChkSum(trama):
    chksum = 0
    for i in range(10):
        chksum = chksum + trama[i]
    chksum = np.uint8(chksum)
    return chksum

def euler_to_quaternion(yaw, pitch, roll):
        qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
        qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
        qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        return [qx, qy, qz, qw]



imuMsg = Imu()
magnetMessage = MagneticField()

imuMsg.orientation_covariance = [ 1e-6, 0, 0,
                           0, 1e-6, 0,
                           0, 0, 1e-6]


imuMsg.angular_velocity_covariance = [1e-6, 0, 0,
                                0 , 1e-6, 0,
                                0 , 0 , 1e-6]


imuMsg.linear_acceleration_covariance = [ 1e-6, 0, 0,
                                   0 , 1e-6, 0,
                                   0 , 0 , 1e-6]




rospy.init_node("imu")
rospy.loginfo("IMU abierto")
pub = rospy.Publisher('imu/data_raw',Imu,queue_size=1)
magnetField = rospy.Publisher('imu/mag_raw',MagneticField,queue_size=100)
rate = rospy.Rate(100)



try:
    #ser=serial.Serial("/dev/ttyUSB1",115200)
    #serialPort = rospy.get_param('imuNode/serial_port') # node_name/argsname
    #print(serialPort)
    # ser=serial.Serial(serialPort,115200)
    ser=serial.Serial("/dev/IMU",115200)
    print("Nodo IMU Lanzado")
    # while(True):
    while(not rospy.is_shutdown()):
        #if ser.in_waiting:
        rx_b= ser.read()
        rx_i=struct.unpack('>B',rx_b)
        rx_i=rx_i[0]
        if(len(trama) == 11):
            trama.pop(0)
            trama.append(rx_i)
            trama_b.pop(0)
            trama_b.append(rx_b)
        else:
            trama.append(rx_i)
            trama_b.append(rx_b)

        if(len(trama) == 11 and trama[0] == 85 and trama[1] == 83):
                chksum = calcularChkSum(trama)

                if(chksum == trama[10]):
                    #print("Angulos")
                    #pintarTrama(trama)
                    rollL = np.int16(trama[2])
                    rollH = np.int16(trama[3])
                    roll = np.int16(((rollH <<8)|rollL))
                    roll_num = np.float(roll/32768.0*180.0)

                    pitchL = np.int16(trama[4])
                    pitchH = np.int16(trama[5])
                    pitch = np.int16(((pitchH <<8)|pitchL))
                    pitch_num = np.float(pitch/32768.0*180.0)

                    yawL = np.int16(trama[6])
                    yawH = np.int16(trama[7])
                    yaw = np.int16(((yawH <<8)|yawL))
                    yaw_num = np.float(yaw/32768.0*180.0)




                    roll=roll_num * degrees2rad
                    pitch=pitch_num * degrees2rad
                    yaw=yaw_num * degrees2rad

                    #print("yaw: "+ str(yaw) + " rad" + "  " + str(yaw_num)+" deg")


                    quaternion = quaternion_from_euler(roll,pitch,yaw)
                    qx = quaternion[0]
                    qy = quaternion[1]
                    qz = quaternion[2]
                    qw = quaternion[3]

                    #trama.clear()
                    ang = 1
                    del trama[:]


        if (len(trama) == 11 and trama[0] == 85 and trama[1] == 82):
                chksum = calcularChkSum(trama)
                if(chksum == trama[10]):
                    #print("Velocidad Angular")
                    # pintarTrama(trama)

                    wxL = np.int16(trama[2])
                    wxH = np.int16(trama[3])
                    wx  = np.int16((wxH <<8)|wxL)
                    wx_num = np.float(wx/32768.0*2000.0)

                    wyL = np.int16(trama[4])
                    wyH = np.int16(trama[5])
                    wy  = np.int16((wyH <<8)|wyL)
                    wy_num = np.float(wy/32768.0*2000.0)

                    wzL = np.int16(trama[6])
                    wzH = np.int16(trama[7])
                    wz  = np.int16((wzH <<8)|wzL)
                    wz_num = np.float(wz/32768.0*2000.0)

                    wx_num = wx_num * math.pi / 180
                    wy_num = wy_num * math.pi / 180
                    wz_num = wz_num * math.pi / 180


                    #trama.clear()
                    vel = 1
                    del trama[:]


        if (len(trama) == 11 and trama[0] == 85 and trama[1] == 81):
                chksum = calcularChkSum(trama)
                if(chksum == trama[10]):
                    #print("Aceleracion")
                    # pintarTrama(trama)
                    AxL = np.int16(trama[2])
                    AxH = np.int16(trama[3])
                    ax  = np.int16((AxH <<8)|AxL)
                    ax_num = np.float(ax/32768.0*16.0*9.8)

                    AyL = np.int16(trama[4])
                    AyH = np.int16(trama[5])
                    ay  = np.int16((AyH <<8)|AyL)
                    ay_num = np.float(ay/32768.0*16.0*9.8)

                    AzL = np.int16(trama[6])
                    AzH = np.int16(trama[7])
                    az  = np.int16((AzH <<8)|AzL)
                    az_num = np.float(az/32768.0*16.0*9.8)


                    #trama.clear()
                    acel = 1
                    del trama[:]
        if (len(trama) == 11 and trama[0] == 85 and trama[1] == 84):
                chksum = calcularChkSum(trama)
                if(chksum == trama[10]):
                    #print("Aceleracion")
                    # pintarTrama(trama)
                    HxL = np.int16(trama[2])
                    HxH = np.int16(trama[3])
                    HyL = np.int16(trama[4])
                    HyH = np.int16(trama[5])
                    HzL = np.int16(trama[6])
                    HzH = np.int16(trama[7])

                    hx  = np.int16((HxH <<8)|HxL)
                    hy  = np.int16((HyH <<8)|HyL)
                    hz  = np.int16((HzH <<8)|HzL)
                    #trama.clear()
                    mag = 1

                    del trama[:]
                        

        if(ang == 1 and vel == 1 and acel ==1 and mag ==1):

                imuMsg.linear_acceleration.x = ax_num
                imuMsg.linear_acceleration.y = ay_num
                imuMsg.linear_acceleration.z = az_num

                imuMsg.angular_velocity.x = wx_num
                imuMsg.angular_velocity.y = wy_num
                imuMsg.angular_velocity.z = wz_num

                imuMsg.orientation.x = qx
                imuMsg.orientation.y = qy
                imuMsg.orientation.z = qz
                imuMsg.orientation.w = qw

                imuMsg.header.stamp = rospy.Time.now()
                # imuMsg.header.frame_id = '/map'
                imuMsg.header.frame_id = 'imu_link'
                imuMsg.header.seq = seq



                magnetMessage.header.frame_id = 'imu_link'
                magnetMessage.header.stamp = rospy.Time.now()
                magnetMessage.magnetic_field.x = np.float(hx)
                magnetMessage.magnetic_field.y = np.float(hy)
                magnetMessage.magnetic_field.z = np.float(hz)
                magnetMessage.header.seq = seq
                magnetField.publish(magnetMessage)


                seq = seq +1


                ang = 0
                vel = 0
                acel = 0
                mag = 0

                pub.publish(imuMsg)
                #print("roll: " + str(roll_num)+"  pitch: "+str(pitch_num)+"  yaw: "+str(yaw_num))
                #print("wx: " + str(wx_num)+"  wy: "+str(wy_num)+"  wz: "+str(wz_num))
                #print("ax: " + str(ax_num)+"  ay: "+str(ay_num)+"  az: "+str(az_num))


except KeyboardInterrupt:
    ser.close()







