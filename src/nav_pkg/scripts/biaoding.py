#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

class CalibrationTool:
    def __init__(self):
        rospy.init_node('calibration_tool_node', anonymous=True)
        self.bridge = CvBridge()
        
        # 使用你测出来的黄金色块参数
        self.lower_red1 = np.array([0, 0, 0]) 
        self.upper_red1 = np.array([20, 255, 117])
        self.lower_red2 = np.array([160, 0, 0])
        self.upper_red2 = np.array([180, 255, 117])
        
        # 强制锁死底盘，发布全零速度
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.debug_pub = rospy.Publisher('/camera/debug_vision', Image, queue_size=1)
        
        rospy.Subscriber("/camera/rgb/image_raw", Image, self.color_callback)
        
        rospy.loginfo("=============================================")
        rospy.loginfo("🛠️ 标定模式已启动！底盘已锁死，请放心测量。")
        rospy.loginfo("1. 请用卷尺将红方块放在距离摄像头正前方刚好 0.25 米处。")
        rospy.loginfo("2. 观察画面或下方日志，记录下此刻的【像素宽度】！")
        rospy.loginfo("=============================================")

        # 持续发布停车指令，防止车子意外滑动
        rospy.Timer(rospy.Duration(0.1), self.keep_still)

    def keep_still(self, event):
        self.cmd_pub.publish(Twist())

    def color_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            return

        blurred = cv2.GaussianBlur(cv_image, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask1, mask2) 
        
        kernel = np.ones((3, 3), np.uint16)
        mask = cv2.erode(mask, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        tracked_img = cv_image.copy()

        # 在画面左上角打上醒目的标定提示
        cv2.putText(tracked_img, "CALIBRATION MODE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 300: 
                x, y, box_w, box_h = cv2.boundingRect(c)
                
                # 画出紧贴的方框
                cv2.rectangle(tracked_img, (x, y), (x + box_w, y + box_h), (0, 255, 0), 2)
                
                # 把像素宽度极其醒目地写在方块旁边
                info_text = "Width: {} px".format(box_w)
                cv2.putText(tracked_img, info_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                
                # 同时在终端里疯狂打印，方便你低头看卷尺的时候余光能扫到
                rospy.loginfo_throttle(0.5, "当前方块像素宽度 w = %d 像素", box_w)

        self.publish_debug_image(tracked_img)

    def publish_debug_image(self, img):
        try:
            self.debug_pub.publish(self.bridge.cv2_to_imgmsg(img, "bgr8"))
        except CvBridgeError:
            pass

if __name__ == '__main__':
    try:
        CalibrationTool()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass