#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

# 仅保留发布对准成功话题的库，方便你在终端监控
from std_msgs.msg import Bool

from astra_common import simplePID

class ColorPIDAlignerStandalone:
    def __init__(self):
        rospy.init_node('color_pid_align_standalone', anonymous=True)
        self.is_shutting_down = False
        rospy.on_shutdown(self.shutdown_hook)

        self.bridge = CvBridge()
        
        # 1. 你的专属防干扰颜色参数
        self.lower_red1 = np.array([0, 130, 60]) 
        self.upper_red1 = np.array([10, 255, 255])
        self.lower_red2 = np.array([170, 130, 60])
        self.upper_red2 = np.array([180, 255, 255])
        
        # 2. 你的专属距离标定参数
        self.target_pixel_x = 320  
        self.target_w = 43         # 🎯 0.25m 处的完美像素宽度
        
        # PID 动力参数
        self.pid_x = simplePID(kp=0.008, ki=0.0, kd=0.001) 
        self.pid_y = simplePID(kp=0.003, ki=0.0, kd=0.0005) 

        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.debug_pub = rospy.Publisher('/camera/debug_vision', Image, queue_size=1)
        self.mask_pub = rospy.Publisher('/camera/debug_mask', Image, queue_size=1)
        
        # 保留成功信号发射器用于调试监控
        self.success_pub = rospy.Publisher('/align_success', Bool, queue_size=1)

        rospy.Subscriber("/camera/rgb/image_raw", Image, self.color_callback)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("👁️ 独立测试版视觉对准节点已启动！")
        rospy.loginfo("当前状态：【火力全开】，只要看到红方块立刻接管底盘！")
        rospy.loginfo("=======================================")

    def shutdown_hook(self):
        self.is_shutting_down = True
        rospy.loginfo("🚨 接收到 Ctrl+C，正在紧急刹车...")
        for _ in range(5):
            self.cmd_pub.publish(Twist())
            rospy.sleep(0.05)

    def color_callback(self, data):
        if self.is_shutting_down: return
        
        # 【已拆除】：原本限制它干活的 if not self.is_tracking_enabled 已经被干掉了！
        # 现在它每收到一帧图像就会直接往下跑！

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            return

        img_height, img_width = cv_image.shape[:2]
        self.target_pixel_x = int(img_width / 2)

        blurred = cv2.GaussianBlur(cv_image, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        mask = cv2.bitwise_or(mask1, mask2) 
        
        kernel = np.ones((3, 3), np.uint16)
        mask = cv2.erode(mask, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        try:
            self.mask_pub.publish(self.bridge.cv2_to_imgmsg(mask, "mono8"))
        except CvBridgeError:
            pass
        
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        center_x, center_y, box_w, box_h = -1, -1, 0, 0
        tracked_img = cv_image.copy()
        valid_target_found = False

        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            # 面积过滤防幽灵噪点
            if cv2.contourArea(c) > 800: 
                x, y, box_w, box_h = cv2.boundingRect(c)
                M = cv2.moments(c)
                if M["m00"] > 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    valid_target_found = True

        if valid_target_found: 
            cv2.rectangle(tracked_img, (x, y), (x + box_w, y + box_h), (0, 255, 0), 2)
            cv2.circle(tracked_img, (center_x, center_y), 5, (0, 0, 255), -1)
            
            info_text = "W:{}px (Target:{}px)".format(box_w, self.target_w)
            cv2.putText(tracked_img, info_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            twist_cmd = self.compute_approach_velocity(center_x, box_w)
            self.cmd_pub.publish(twist_cmd)
        else:
            self.pid_x.reset()
            self.pid_y.reset()
            if not self.is_shutting_down:
                self.cmd_pub.publish(Twist())

        self.publish_debug_image(tracked_img)

    def publish_debug_image(self, img):
        try:
            self.debug_pub.publish(self.bridge.cv2_to_imgmsg(img, "bgr8"))
        except CvBridgeError:
            pass

    def compute_approach_velocity(self, current_x, current_w):
        twist = Twist()
        
        error_pixel_y = self.target_pixel_x - current_x    
        error_width_x = self.target_w - current_w          

        # 安全锁：超限防撞
        if current_w > (self.target_w + 15):
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            self.pid_x.reset() 
            self.pid_y.reset()
            rospy.logwarn_throttle(0.5, "🛑 [安全保护触发] 像素超限(W:%d)！防撞强制停车！", current_w)
            return twist

        # =======================================================
        # 【传家宝参数区】
        # =======================================================
        Y_TOLERANCE_COARSE = 40   # 左右误差大于 40 就不许往前走
        Y_TOLERANCE_FINE = 4      # 抓取前的精调，必须控制在 4 像素以内 
        X_TOLERANCE = 2           # 前后误差允许范围缩紧到 2 个像素以内
        # =======================================================

        vel_y = self.pid_y.compute(0, -error_pixel_y)
        vel_y = max(min(vel_y, 0.15), -0.15) 

        vel_x = self.pid_x.compute(0, -error_width_x)
        vel_x = max(min(vel_x, 0.15), -0.15) 

        if abs(error_pixel_y) > Y_TOLERANCE_COARSE:
            twist.linear.x = 0.0
            twist.linear.y = vel_y
            rospy.loginfo_throttle(0.5, "-> [1. 粗调] 偏离太大，正在横移... Y误差: %d", error_pixel_y)
            
        elif abs(error_width_x) > X_TOLERANCE:
            twist.linear.x = vel_x
            twist.linear.y = vel_y 
            rospy.loginfo_throttle(0.5, "-> [2. 逼近] 前进/后退中... 当前W: %d, 目标W: %d", current_w, self.target_w)
            
        elif abs(error_pixel_y) > Y_TOLERANCE_FINE:
            twist.linear.x = 0.0
            twist.linear.y = vel_y
            rospy.loginfo_throttle(0.5, "-> [3. 精调] 消除微小横向偏差... Y误差: %d", error_pixel_y)
            
        else:
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            rospy.loginfo_throttle(1.0, "🎯 [终极锁定] 前后左右零误差！锁定目标！")
            
            # 持续发射成功信号，可以配合 rqt 或 rostopic 监控
            self.success_pub.publish(True)

        return twist

if __name__ == '__main__':
    try:
        ColorPIDAlignerStandalone()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass