#!/usr/bin/env python


import rospy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist 
from geometry_msgs.msg import Vector3Stamped

import serial
import time
import array
import sys
import numpy as np
import math
import struct
import os



class WI901C():
    def  __init__(self):
        # os.system("echo 'nvidia' | sudo -S chmod 666 /dev/IMU")
        # self.ser=serial.Serial("/dev/IMU",115200)
        self.degrees2rad = math.pi/180.0

    def closeSerial(self):
        self.ser.close()

    def pintarTrama(self,trama):
        k = ""
        for i in trama:
            k = k + " " +  str(i)
        print(k)

    def calcularChkSum(self,trama):
        chksum = 0
        for i in range(10):
            chksum = chksum + trama[i]
        chksum = np.uint8(chksum)   
        return chksum

    def readAngles(self):
        self.ser.flushInput()
        correctWeft = False
        trama = [] #Trama de enteros
        trama_b =[] #Trama de bytes
        while(correctWeft == False):
            if self.ser.in_waiting:
                rx_b= self.ser.read()
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
                # self.pintarTrama(trama)
                if(len(trama) == 11 and trama[0] == 85 and trama[1] == 83):
                    chksum = self.calcularChkSum(trama)
                    if(chksum == trama[10]):
                        rollL = np.int16(trama[2])
                        rollH = np.int16(trama[3])
                        roll = np.int16(((rollH <<8)|rollL))
                        roll_deg = np.float(roll/32768.0*180.0)

                        pitchL = np.int16(trama[4])
                        pitchH = np.int16(trama[5])
                        pitch = np.int16(((pitchH <<8)|pitchL))
                        pitch_deg = np.float(pitch/32768.0*180.0)

                        yawL = np.int16(trama[6])
                        yawH = np.int16(trama[7])
                        yaw = np.int16(((yawH <<8)|yawL))
                        yaw_deg = np.float(yaw/32768.0*180.0)


                        roll_rad=roll_deg * self.degrees2rad
                        pitch_rad=pitch_deg * self.degrees2rad
                        yaw_rad=yaw_deg * self.degrees2rad


                        del trama[:]
                        correctWeft = True
                        return(roll_deg,pitch_deg,yaw_deg)





class scout_mini():
    def  __init__(self):
        rospy.init_node('moveAgilex', anonymous=True)
        self.rate = rospy.Rate(10) # 10hz
        self.movePub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        rospy.Subscriber("imu/rpy/filtered", Vector3Stamped, self.imu)
        self.roll=0.0
        self.pitch=0.0
        self.yaw=0.0
        self.dead=0

    def sum(self,a,b):
        sum = a + b
        if(sum > 360):
            sum = sum - 360
        return sum


    def up(self,time):
        movement = Twist()
        movement.linear.x = 0.5
        self.move(movement,time)

    def rotateRight(self,time):
        movement = Twist()
        movement.angular.z = 0.2
        self.move(movement,time)


    def rotateLeft(self,time):
        movement = Twist()
        movement.angular.z = -0.5
        self.move(movement,time)


    def move(self,movement,time):
        now = rospy.Time.now()
        while rospy.Time.now() < now + rospy.Duration.from_sec(time):
            self.movePub.publish(movement)
            self.rate.sleep() 

    def imu(self,data):
        # print(data)
        roll=(180.0/math.pi)*data.vector.x
        if(roll<0):
            self.roll=roll+360.0
        else:
            self.roll=roll


        pitch=(180.0/math.pi)*data.vector.y
        if(pitch<0):
            self.pitch=pitch+360.0
        else:
            self.pitch=pitch

        yaw=(180.0/math.pi)*data.vector.z
        if(yaw<0):
            self.yaw=yaw+360.0
        else:
            self.yaw=yaw
        

    def checkImu(self):
        time.sleep(2)
        yawStart=self.yaw
        umbral=4
        limSup=90+umbral/2
        limInf=90-umbral/2
        print("------------------------------------------------------------")
        print("yaw inicial:  " +str(yawStart))
        vmin=self.sum(yawStart,limInf)
        vmax=self.sum(yawStart,limSup)
        print("Rango objetivo: " +str(vmin)+","+str(vmax))
        while(not((vmin <self.yaw) and  (self.yaw < vmax)) and (not rospy.is_shutdown())):
                robot.rotateRight(0.1)               
                print("yaw :  " + str(self.yaw)+ "   " + str(self.yaw>vmin)+ "   "  +  str(self.yaw<vmax))
        print("Objetivo 1 Alcanzado")

        time.sleep(2)

        yawStart=self.yaw
        print("------------------------------------------------------------")
        print("yaw inicial:  " +str(yawStart))
        vmin=self.sum(yawStart,limInf)
        vmax=self.sum(yawStart,limSup)
        print("Rango objetivo: " +str(vmin)+","+str(vmax))
        while(not((vmin <self.yaw) and  (self.yaw < vmax)) and (not rospy.is_shutdown())):
                robot.rotateRight(0.1)
                print("yaw :  " + str(self.yaw)+ "   " + str(self.yaw>vmin)+ "   "  +  str(self.yaw<vmax))
        print("Objetivo 2 Alcanzado")

        time.sleep(2)

        yawStart=self.yaw
        print("------------------------------------------------------------")
        print("yaw inicial:  " +str(yawStart))
        vmin=self.sum(yawStart,limInf)
        vmax=self.sum(yawStart,limSup)
        print("Rango objetivo: " +str(vmin)+","+str(vmax))
        while(not((vmin <self.yaw) and  (self.yaw < vmax)) and (not rospy.is_shutdown())):
                robot.rotateRight(0.1)
                print("yaw :  " + str(self.yaw)+ "   " + str(self.yaw>vmin)+ "   "  +  str(self.yaw<vmax))
        print("Objetivo 3 Alcanzado")

        time.sleep(2)

        yawStart=self.yaw
        print("------------------------------------------------------------")
        print("yaw inicial:  " +str(yawStart))
        vmin=self.sum(yawStart,limInf)
        vmax=self.sum(yawStart,limSup)
        print("Rango objetivo: " +str(vmin)+","+str(vmax))
        while(not((vmin <self.yaw) and  (self.yaw < vmax)) and (not rospy.is_shutdown())):
                robot.rotateRight(0.1)
                print("yaw :  " + str(self.yaw)+ "   " + str(self.yaw>vmin)+ "   "  +  str(self.yaw<vmax))
        print("Objetivo 4 Alcanzado")
try:
    #imu =  WI901C()
    robot = scout_mini()
    robot.checkImu()
    # while(not rospy.is_shutdown()):
    #     time.sleep(1)
    # [roll,pitch,yaw_start]=imu.readAngles()
    # yaw_act = yaw_start
    # print("yaw inicial:  " +str(yaw_start))
    # vmin=sum(yaw_start,88)
    # vmax=sum(yaw_start,92)
    # print("Rango objetivo: " +str(vmin)+","+str(vmax))
    # print(vmin > yaw_act)
    # print(yaw_act < vmax)
    # while(not((vmin < yaw_act) and  (yaw_act < vmax)) and (not rospy.is_shutdown())):
    #         robot.rotateRight(0.1)
    #         [roll,pitch,yaw_act]=imu.readAngles()
    #         print("yaw :  " + str(yaw_act))
    # print("Objetivo 1 Alcanzado")


    # time.sleep(5)

    # yaw_act = sum(yaw_start,90)
    # print("yaw inicial:  " +str(yaw_act))
    # vmin=sum(yaw_act,88)
    # vmax=sum(yaw_act,92)
    # print("Rango objetivo: " +str(vmin)+","+str(vmax))
    # print(vmin > yaw_act)
    # print(yaw_act < vmax)
    # while(not((vmin < yaw_act) and  (yaw_act < vmax)) and (not rospy.is_shutdown())):
    #         robot.rotateRight(0.1)
    #         [roll,pitch,yaw_act]=imu.readAngles()
    #         print("yaw :  " + str(yaw_act))
    # print("Objetivo 2 Alcanzado")


    # time.sleep(5)


    # yaw_act = sum(yaw_start,180)
    # print("yaw inicial:  " +str(yaw_act))
    # vmin=sum(yaw_act,88)
    # vmax=sum(yaw_act,92)
    # print("Rango objetivo: " +str(vmin)+","+str(vmax))
    # print(vmin > yaw_act)
    # print(yaw_act < vmax)
    # while(not((vmin < yaw_act) and  (yaw_act < vmax)) and (not rospy.is_shutdown())):
    #         robot.rotateRight(0.1)
    #         [roll,pitch,yaw_act]=imu.readAngles()
    #         print("yaw :  " + str(yaw_act))
    # print("Objetivo 3 Alcanzado")


    # time.sleep(5)


    # yaw_act = sum(yaw_start,270)
    # print("yaw inicial:  " +str(yaw_act))
    # vmin=sum(yaw_act,88)
    # vmax=sum(yaw_act,92)
    # print("Rango objetivo: " +str(vmin)+","+str(vmax))
    # print(vmin > yaw_act)
    # print(yaw_act < vmax)
    # while(not((vmin < yaw_act) and  (yaw_act < vmax)) and (not rospy.is_shutdown())):
    #         robot.rotateRight(0.1)
    #         [roll,pitch,yaw_act]=imu.readAngles()
    #         print("yaw :  " + str(yaw_act))
    # print("Objetivo 4 Alcanzado")
except KeyboardInterrupt:
    pass
#    imu.closeSerial()










