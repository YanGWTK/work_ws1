#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import cv2.aruco as aruco
import numpy as np
from sensor_msgs.msg import Image
from std_srvs.srv import Trigger, TriggerResponse

class ArUcoScannerService:
    def __init__(self):
        rospy.init_node('aruco_scanner_node', anonymous=True)
        
        # 调试画板
        self.debug_pub = rospy.Publisher('/camera/debug_qr', Image, queue_size=1)
        
        # 1. 👑 锁定目标家族：既然测出来是 5x5_250，我们就只盯死这一个！速度最快！
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
        self.aruco_params = aruco.DetectorParameters_create()
        
        # 2. 声明 ROS 服务
        self.srv = rospy.Service('/scan_qr', Trigger, self.handle_scan_request)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("👑 [降维打击版] ArUco 工业视觉服务已就绪！")
        rospy.loginfo("🎯 锁定家族: DICT_5X5_250")
        rospy.loginfo("🎥 监听话题: /camera/rgb/image_raw (底盘主相机)")
        rospy.loginfo("💤 随时等待指令，一旦启动将开启 30 秒死磕模式...")
        rospy.loginfo("=======================================")

    def manual_imgmsg_to_cv2(self, img_msg):
        """手撕 ROS 图像，绕开 cv_bridge 冲突"""
        image_np = np.frombuffer(img_msg.data, dtype=np.uint8).reshape(img_msg.height, img_msg.width, -1)
        if "rgb8" in img_msg.encoding:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        elif "yuv" in img_msg.encoding or "yuyv" in img_msg.encoding:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_YUV2BGR_YUYV)
        return image_np

    def handle_scan_request(self, req):
        rospy.loginfo("=======================================")
        rospy.loginfo("📷 收到大老板指令！开启 ArUco 探测雷达...")
        
        start_time = rospy.Time.now()
        timeout = rospy.Duration(30.0) 
        scan_count = 0 

        while (rospy.Time.now() - start_time) < timeout:
            try:
                # 拿取主相机最新画面
                img_msg = rospy.wait_for_message("/camera/rgb/image_raw", Image, timeout=1.0)
                cv_image = self.manual_imgmsg_to_cv2(img_msg)
                debug_img = cv_image.copy()
                gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
                
                scan_count += 1
                
                # 🎯 核心大招：一句话破解标签
                corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)
                
                if ids is not None and len(ids) > 0:
                    # 我们取画面里看到的第一个标签的 ID
                    target_id = str(ids[0][0]) 
                    time_cost = (rospy.Time.now() - start_time).to_sec()
                    
                    rospy.loginfo("✅ 锁定目标！历经 %d 帧，耗时 %.1f 秒。目标 ID: [%s]", scan_count, time_cost, target_id)
                    
                    # 画出极其专业的四边形彩色边框和 ID
                    aruco.drawDetectedMarkers(debug_img, corners, ids)
                    
                    # 打包发送给调试频道
                    debug_msg = Image()
                    debug_msg.header = img_msg.header
                    debug_msg.height, debug_msg.width, _ = debug_img.shape
                    debug_msg.encoding = "bgr8"
                    debug_msg.step = debug_img.shape[1] * 3
                    debug_msg.data = debug_img.tobytes()
                    self.debug_pub.publish(debug_msg)
                    
                    # ✨ 成功拿到 ID，向上级汇报！(注意：这里返回的是数字的字符串，比如 "1")
                    return TriggerResponse(success=True, message=target_id)
                
                else:
                    # 没扫到，喘息一下继续扫
                    rospy.sleep(0.05)
                    
            except rospy.ROSException:
                rospy.logwarn("⚠️ 等待底盘相机画面中...")
            except Exception as e:
                rospy.logerr("❌ 图像处理失败: %s", e)
                return TriggerResponse(success=False, message="CV_ERROR")

        rospy.logerr("❌ 30秒超时！未能找到任何 ArUco 标签，任务流产！")
        return TriggerResponse(success=False, message="TIMEOUT_NO_QR")

if __name__ == '__main__':
    try:
        ArUcoScannerService()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass