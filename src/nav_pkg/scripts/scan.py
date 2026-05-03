#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import cv2.aruco as aruco
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import Bool
from std_srvs.srv import SetBool, SetBoolResponse

class ArucoSearchNode:
    def __init__(self, scan_mode=0):
        rospy.init_node('aruco_search_node', anonymous=True)
        rospy.on_shutdown(self.cleanup)
        
        self.bridge = CvBridge()
        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.debug_pub = rospy.Publisher('/camera/debug_vision', Image, queue_size=1)
        
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
        self.aruco_params = aruco.DetectorParameters_create()
        self.target_id = 2
        # self.target_id = rospy.get_param('/current_aruco_id', 1)
        # 螃蟹步参数
        if scan_mode == 0:
            self.dir_name = "从左到右 (向右横移)"
            self.speed_y = -0.1  
            self.hud_text = "Searching RIGHT for ID 2..."
        else:
            self.dir_name = "从右到左 (向左横移)"
            self.speed_y = 0.1   
            self.hud_text = "Searching LEFT for ID 2..."

        # =========================================================
        # 【SMACH 联动接口】
        # =========================================================
        self.is_searching = False
        self.search_done = False # 🌟 新增：任务完成标记位
        self.toggle_srv = rospy.Service('/enable_search', SetBool, self.toggle_cb)
        self.success_pub = rospy.Publisher('/search_success', Bool, queue_size=1)

        rospy.Subscriber("/camera/rgb/image_raw", Image, self.vision_callback)

        rospy.loginfo("=======================================")
        rospy.loginfo("🦀 [独立节点] 螃蟹步粗调索敌雷达已启动！")
        rospy.loginfo("🎯 策略升级：居中刹车 + 防漏接持续呼叫机制！")
        rospy.loginfo("当前状态：💤【休眠中】，等待 SMACH 唤醒...")
        rospy.loginfo("=======================================")

    def toggle_cb(self, req):
        self.is_searching = req.data
        if self.is_searching:
            self.target_id = rospy.get_param('/current_aruco_id', 1)
            rospy.loginfo("👁️ 收到唤醒指令！开始执行: %s", self.dir_name)
            self.search_done = False # 🌟 每次唤醒，必须重置完成状态
        else:
            rospy.loginfo("💤 收到休眠指令！SMACH 已接管，索敌雷达关闭。")
            self.vel_pub.publish(Twist())
        return SetBoolResponse(success=True, message="Search Status Changed")

    def cleanup(self):
        self.vel_pub.publish(Twist())
        rospy.loginfo("✅ 索敌节点安全退出！")

    def vision_callback(self, data):
        # 如果大老板没让开机，坚决不干活
        if not self.is_searching: 
            return

        # 🌟 核心防漏接机制：如果已经找准并停稳了，持续轰炸 SMACH！
        if getattr(self, 'search_done', False):
            self.success_pub.publish(True)
            rospy.loginfo_throttle(2.0, "📡 [防漏接] 目标已在视野正中！正在持续向 SMACH 发送交接信号...")
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            return

        # 获取画面宽度，计算正中心 X 坐标
        img_width = cv_image.shape[1]
        image_center_x = img_width / 2
        
        # 🌟 核心设定：中心容差区域 (比如 640 宽度，容差 80 就是 240~400 之间)
        tolerance = 80 

        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)
        debug_img = cv_image.copy()

        if ids is not None and len(ids) > 0 and self.target_id in ids.flatten().tolist():
            idx = ids.flatten().tolist().index(self.target_id)
            target_corner = corners[idx][0]
            
            # 计算二维码在画面里的实际 X 坐标
            center_x = int(np.mean(target_corner[:, 0]))
            
            aruco.drawDetectedMarkers(debug_img, [corners[idx]], np.array([[self.target_id]]))
            
            # 判断是否进入了“黄金中心区域”
            if abs(center_x - image_center_x) <= tolerance:
                # 🎯 进中心了！紧急刹车！
                self.vel_pub.publish(Twist())
                cv2.putText(debug_img, "CENTERED & LOCKED!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 先把画满绿色字体的图像发出去，让监控端看到
                try: self.debug_pub.publish(self.bridge.cv2_to_imgmsg(debug_img, "bgr8"))
                except: pass
                
                # 刹车缓冲，消除惯性
                rospy.loginfo("🛑 目标已进入中心区域！刹车等待 1.5 秒消除物理惯性...")
                rospy.sleep(1.5)
                
                # 🌟 标记完成！接下来交给头部的“防漏接机制”去持续呼叫 SMACH
                rospy.loginfo("🎯 底盘已完全停稳，开始呼叫 SMACH 移交控制权！")
                self.search_done = True 
                return # 结束本次回调
                
            else:
                # 👀 发现目标，但还在边缘，继续往前蹭一蹭
                search_twist = Twist()
                search_twist.linear.y = self.speed_y 
                self.vel_pub.publish(search_twist)
                cv2.putText(debug_img, "Target Found! Centering...", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                
        else:
            # 🦀 彻底没找到，正常横移
            search_twist = Twist()
            search_twist.linear.y = self.speed_y 
            self.vel_pub.publish(search_twist)
            cv2.putText(debug_img, self.hud_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # 发布正常情况下的监控图像
        try:
            self.debug_pub.publish(self.bridge.cv2_to_imgmsg(debug_img, "bgr8"))
        except:
            pass

if __name__ == '__main__':
    try:
        # 0 = 从左往右找
        ArucoSearchNode(scan_mode=0)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass