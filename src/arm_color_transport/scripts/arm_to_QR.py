#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Int32, String, Bool
    
def intCallback(msg):
    rospy.loginfo("Received integer: %d", msg.data)
def arm_to_QR():
    rospy.init_node('arm_to_QR', anonymous=True)
    rospy.Subscriber("/arm_control", Int32, intCallback)
    rospy.spin()
if __name__ == '__main__':
    arm_to_QR()

