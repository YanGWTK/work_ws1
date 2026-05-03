#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import cv2.aruco as aruco
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

from astra_common import simplePID

class ArucoPIDAlignerTest:
    def __init__(self):
        rospy.init_node('aruco_pid_align_test_node', anonymous=True)
        self.is_shutting_down = False
        rospy.on_shutdown(self.shutdown_hook)

        self.bridge = CvBridge()
        
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
        self.aruco_params = aruco.DetectorParameters_create()
        self.target_id = 2  
        
        self.target_pixel_x = 320  
        self.target_w = 79  
        
        self.pid_x = simplePID(kp=0.006, ki=0.0, kd=0.001) 
        self.pid_y = simplePID(kp=0.004, ki=0.0, kd=0.0005) 
        self.pid_z = simplePID(kp=0.005, ki=0.0, kd=0.001)

        self.lost_frame_count = 0     
        self.max_lost_frames = 5      
        self.last_twist = Twist()     
        self.blind_move_done = False

        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.debug_pub = rospy.Publisher('/camera/debug_vision', Image, queue_size=1)

        rospy.Subscriber("/camera/rgb/image_raw", Image, self.vision_callback)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("🚀 [全空间垂直版] 3-DoF 视觉 PID 已启动！")
        rospy.loginfo("🎯 终极设定：对准后将盲开突刺 20cm！")
        rospy.loginfo("=======================================")

    def shutdown_hook(self):
        self.is_shutting_down = True
        rospy.loginfo("🚨 接收到 Ctrl+C，正在紧急刹车...")
        for _ in range(5):
            self.cmd_pub.publish(Twist())
            rospy.sleep(0.05)

    def execute_blind_forward(self, distance=0.1, speed=0.1):
        self.cmd_pub.publish(Twist())
        rospy.sleep(0.5)
        duration = distance / speed
        dash_twist = Twist()
        dash_twist.linear.x = speed
        rospy.loginfo("🚀 车头已绝对垂直！启动盲开突刺 (%.2f m/s, %d cm)...", speed, distance*100)
        start_time = rospy.get_time()
        while rospy.get_time() - start_time < duration:
            if self.is_shutting_down: break
            self.cmd_pub.publish(dash_twist)
            rospy.sleep(0.05)
        self.cmd_pub.publish(Twist())
        rospy.loginfo("✅ %d cm 垂直盲开完毕！底盘已死锁，准备下爪！", distance*100)

    def vision_callback(self, data):
        if self.is_shutting_down or self.blind_move_done: return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            return

        img_height, img_width = cv_image.shape[:2]
        self.target_pixel_x = int(img_width / 2)

        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)

        center_x, center_y, box_w = -1, -1, 0
        tracked_img = cv_image.copy()
        valid_target_found = False

        if ids is not None and len(ids) > 0 and self.target_id in ids.flatten().tolist():
            idx = ids.flatten().tolist().index(self.target_id)
            target_corner = corners[idx][0] 
            
            center_x = int(np.mean(target_corner[:, 0]))
            center_y = int(np.mean(target_corner[:, 1]))
            
            min_x = np.min(target_corner[:, 0])
            max_x = np.max(target_corner[:, 0])
            box_w = int(max_x - min_x)
            
            valid_target_found = True

        if valid_target_found: 
            self.lost_frame_count = 0
            aruco.drawDetectedMarkers(tracked_img, [corners[idx]], np.array([[self.target_id]]))
            cv2.circle(tracked_img, (center_x, center_y), 5, (0, 0, 255), -1)
            
            info_text = "W:{}px".format(box_w)
            cv2.putText(tracked_img, info_text, (int(min_x), int(np.min(target_corner[:, 1])) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            twist_cmd = self.compute_approach_velocity(center_x, box_w, target_corner)
            self.last_twist = twist_cmd
            
            if not self.blind_move_done:
                self.cmd_pub.publish(twist_cmd)
            
        else:
            self.lost_frame_count += 1
            if self.lost_frame_count >= self.max_lost_frames:
                self.pid_x.reset()
                self.pid_y.reset()
                self.pid_z.reset()
                if not self.is_shutting_down and not self.blind_move_done:
                    self.cmd_pub.publish(Twist()) 
                cv2.putText(tracked_img, "Target Lost! Stopped.", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                if not self.is_shutting_down and not self.blind_move_done:
                    self.cmd_pub.publish(self.last_twist)
                cv2.putText(tracked_img, "Blur Compensating...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

        self.publish_debug_image(tracked_img)

    def publish_debug_image(self, img):
        try:
            self.debug_pub.publish(self.bridge.cv2_to_imgmsg(img, "bgr8"))
        except CvBridgeError:
            pass

    def compute_approach_velocity(self, current_x, current_w, corners):
        twist = Twist()
        
        error_pixel_y = self.target_pixel_x - current_x    
        error_width_x = self.target_w - current_w          

        left_edge_height = np.linalg.norm(corners[0] - corners[3])
        right_edge_height = np.linalg.norm(corners[1] - corners[2])
        error_yaw = left_edge_height - right_edge_height 

        if current_w > (self.target_w + 30):
            twist.linear.x = 0.0; twist.linear.y = 0.0; twist.angular.z = 0.0
            self.pid_x.reset(); self.pid_y.reset(); self.pid_z.reset()
            rospy.logwarn_throttle(0.5, "🛑 像素超限！防撞强制停车！")
            return twist

        Y_TOLERANCE_COARSE = 40   
        Y_TOLERANCE_FINE = 4      
        X_TOLERANCE = 2           
        YAW_TOLERANCE = 2.0  

        vel_y = self.pid_y.compute(0, -error_pixel_y)
        vel_y = max(min(vel_y, 0.15), -0.15) 

        vel_x = self.pid_x.compute(0, -error_width_x)
        vel_x = max(min(vel_x, 0.15), -0.15) 
        
        vel_z = self.pid_z.compute(0, -error_yaw)
        vel_z = max(min(vel_z, 0.2), -0.2) 

        if abs(error_pixel_y) > Y_TOLERANCE_COARSE:
            twist.linear.x = 0.0
            twist.linear.y = vel_y
            rospy.loginfo_throttle(0.5, "-> [1. 粗调] 偏离太大，正在横移...")
            
        elif abs(error_width_x) > X_TOLERANCE:
            twist.linear.x = vel_x
            twist.linear.y = vel_y 
            rospy.loginfo_throttle(0.5, "-> [2. 逼近] 前进/后退调整距离...")
            
        elif abs(error_pixel_y) > Y_TOLERANCE_FINE:
            twist.linear.x = 0.0
            twist.linear.y = vel_y
            rospy.loginfo_throttle(0.5, "-> [3. 精调] 消除微小横向偏差...")
            
        elif abs(error_yaw) > YAW_TOLERANCE:
            twist.linear.x = 0.0
            twist.linear.y = vel_y  
            twist.angular.z = vel_z
            rospy.loginfo_throttle(0.5, "-> [4. 摆正车头] 正在原地扭正垂直角... 偏差: %.1f", error_yaw)
            
        else:
            if not self.blind_move_done:
                rospy.loginfo("🎯 [终极锁定] 前后、左右、车头方向 3D 零误差！！")
                # 🌟 核心修改点：这里传入 distance=0.2 也就是 20cm
                self.execute_blind_forward(distance=0.15, speed=0.1)
                self.blind_move_done = True
                
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.angular.z = 0.0

        return twist

if __name__ == '__main__':
    try:
        ArucoPIDAlignerTest()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass