#!/usr/bin/env python3
# encoding: utf-8
#import rospy
from Rosmaster_Lib import Rosmaster
#from std_msgs.msg import Int32, String, Bool
from time import sleep, time

def arm_servo(s1, s2, s3, s4, s5, s6):
    bot.set_uart_servo_angle_array([s1, s2, s3, s4, s5, s6])
    return s1, s2, s3, s4, s5, s6

def arm_control():
    rospy.init_node('arm_control', anonymous=True)
    arm_con_ser = rospy.Publisher('/arm_control',Int32, queue_size=10)
    rate = rospy.Rate(10) 
    counter = 0
    publish_active = True
    while not rospy.is_shutdown():
       if publish_active:
          arm_msg = Int32()
          arm_msg.data = counter
          arm_con_ser.publish(arm_msg)
          rospy.loginfo("Sent command: %d", arm_msg.data)
          counter += 1
          if counter>=10:
             publish_active = False
          rate.sleep()

if __name__ == '__main__':
        
   # arm_control()

    bot = Rosmaster()  # ´´½¨Rosmaster¶ÔÏó bot Create the Rosmaster object bot
    bot.create_receive_threading()  # Æô¶¯½ÓÊÕÊý¾Ý Start receiving data

    arm_servo(90,160,5,0,90,1)
    sleep(2)
    arm_servo(90,109,24,5,90,1)  #
    sleep(2)
    arm_servo(90,109,24,5,90,134)
    sleep(2)
    arm_servo(90,160,5,0,90,134)
    sleep(2)
    arm_servo(90,109,24,5,90,134)
    sleep(2)
    arm_servo(90,109,24,5,90,1)
    sleep(2)
    arm_servo(90,160,5,0,90,1)
    sleep(2)
    
    read_array = bot.get_uart_servo_angle_array() #Ò»´ÎÐÔ¶ÁÈ¡Áù¸ö¶æ»úµÄ½Ç¶È
    print("read array:", read_array)

