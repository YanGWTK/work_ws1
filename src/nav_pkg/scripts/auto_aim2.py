#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import cv2.aruco as aruco
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

# 🌟 新增：引入布尔类型和服务接口，用于和 SMACH 通信
from std_msgs.msg import Bool
from std_srvs.srv import SetBool, SetBoolResponse

from astra_common import simplePID

class ArucoPIDAligner:
    def __init__(self):
        rospy.init_node('aruco_pid_align_node', anonymous=True)
        self.is_shutting_down = False
        rospy.on_shutdown(self.shutdown_hook)

        self.bridge = CvBridge()
        
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
        self.aruco_params = aruco.DetectorParameters_create()
        self.target_id = 2
        
        self.target_pixel_x = 320  
        self.target_w = 78  
        
        self.pid_x = simplePID(kp=0.008, ki=0.0, kd=0.001) 
        self.pid_y = simplePID(kp=0.004, ki=0.0, kd=0.0005) 
        # 已删除 pid_z

        self.lost_frame_count = 0     
        self.max_lost_frames = 5      
        self.last_twist = Twist()     
        self.blind_move_done = False

        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.debug_pub = rospy.Publisher('/camera/debug_vision', Image, queue_size=1)

        # =========================================================
        # 【SMACH 联动通信接口】
        # =========================================================
        # 1. 视觉开关，默认【关闭】！防止在前往桌子的路上和 move_base 抢夺底盘
        self.is_tracking_enabled = False
        self.toggle_srv = rospy.Service('/enable_align', SetBool, self.toggle_cb)
        
        # 2. 成功信号发射器 (用来告诉大老板 SMACH "我抓取距离对好了")
        self.success_pub = rospy.Publisher('/align_success', Bool, queue_size=1)
        # =========================================================

        rospy.Subscriber("/camera/rgb/image_raw", Image, self.vision_callback)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("🛡️ [SMACH受控版] 2-DoF 视觉对准节点已启动！")
        rospy.loginfo("当前状态：💤【休眠中】，等待 SMACH 唤醒...")
        rospy.loginfo("=======================================")

    def toggle_cb(self, req):
        """处理 SMACH 发来的开启/关闭视觉请求"""
        self.is_tracking_enabled = req.data
        if self.is_tracking_enabled:
            self.target_id = rospy.get_param('/current_aruco_id', 1)
            rospy.loginfo("👁️ 收到 SMACH 唤醒指令！视觉对准已【开启】！接管底盘！")
            # 开启时重置所有状态，准备迎接新任务
            self.pid_x.reset()
            self.pid_y.reset()
            self.lost_frame_count = 0
            self.blind_move_done = False # 🌟 核心：重置盲开锁
        else:
            rospy.loginfo("💤 收到 SMACH 休眠指令！视觉对准已【关闭】！交出底盘！")
            self.cmd_pub.publish(Twist())
            
        return SetBoolResponse(success=True, message="Status Changed")

    def shutdown_hook(self):
        self.is_shutting_down = True
        rospy.loginfo("🚨 接收到 Ctrl+C，正在紧急刹车...")
        for _ in range(5):
            self.cmd_pub.publish(Twist())
            rospy.sleep(0.05)

    def execute_blind_forward(self, distance=0.15, speed=0.1):
        self.cmd_pub.publish(Twist())
        rospy.sleep(0.5)
        duration = distance / speed
        dash_twist = Twist()
        dash_twist.linear.x = speed
        rospy.loginfo("🚀 启动盲开突刺 (%.2f m/s, %d cm)...", speed, distance*100)
        start_time = rospy.get_time()
        while rospy.get_time() - start_time < duration:
            if self.is_shutting_down: break
            self.cmd_pub.publish(dash_twist)
            rospy.sleep(0.05)
        self.cmd_pub.publish(Twist())
        rospy.loginfo("✅ %d cm 垂直盲开完毕！底盘已死锁，准备下爪！", distance*100)

    def vision_callback(self, data):
        # 🌟 核心拦截：如果 SMACH 没下令开启，坚决不干活，直接跳出！
        if not self.is_tracking_enabled or self.is_shutting_down: 
            return

        # 2. 🌟 核心修复：如果活已经干完了，不要直接 return，而是持续轰炸发信号！
        if self.blind_move_done:
            self.success_pub.publish(True)
            rospy.loginfo_throttle(2.0, "📡 [防漏接机制] 突刺已完成！正在持续向 SMACH 发送交接信号...")
            return

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
                if not self.is_shutting_down and not self.blind_move_done:
                    # ===================================================
                    # 🌟 核心修改：主动索敌！找不到就原地自转扫视！
                    # ===================================================
                    search_twist = Twist()
                    search_twist.angular.z = 0.3  # 以 0.3 的角速度向左持续旋转找码
                    self.cmd_pub.publish(search_twist) 
                    
                cv2.putText(tracked_img, "Searching Target...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
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

        if current_w > (self.target_w + 50):
            twist.linear.x = 0.0; twist.linear.y = 0.0; twist.angular.z = 0.0
            self.pid_x.reset(); self.pid_y.reset()
            rospy.logwarn_throttle(0.5, "🛑 像素超限！防撞强制停车！")
            return twist

        Y_TOLERANCE_COARSE = 40   
        Y_TOLERANCE_FINE = 4      
        X_TOLERANCE = 2           

        vel_y = self.pid_y.compute(0, -error_pixel_y)
        vel_y = max(min(vel_y, 0.15), -0.15) 

        vel_x = self.pid_x.compute(0, -error_width_x)
        vel_x = max(min(vel_x, 0.15), -0.15) 

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
            
        else:
            if not self.blind_move_done:
                rospy.loginfo("🎯 [终极锁定] 前后、左右 2D 零误差！！")
                
                # 执行盲开突刺 (15cm)
                self.execute_blind_forward(distance=0.15, speed=0.1)
                self.blind_move_done = True
                
                # 🌟 核心回调：向 SMACH 大老板发射成功信号！
                rospy.loginfo("📡 任务完成，发射信号给 SMACH 状态机！")
                self.success_pub.publish(True)
                
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.angular.z = 0.0

        return twist

if __name__ == '__main__':
    try:
        ArucoPIDAligner()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass