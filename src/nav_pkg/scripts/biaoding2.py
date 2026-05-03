#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import cv2.aruco as aruco
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class ArucoVisualizer:
    def __init__(self):
        rospy.init_node('aruco_visualizer', anonymous=True)
        
        # ROS 图像转换桥梁，用于 OpenCV 和 ROS 图像格式互转
        self.bridge = CvBridge()
        
        # 锁定咱们特定的 2 号标签家族和 ID
        # Yahboom 和主流教程一般默认用这个 5x5_250 家族
        self.aruco_dict = aruco.Dictionary_get(aruco.DICT_5X5_250)
        self.aruco_params = aruco.DetectorParameters_create()
        self.target_id = 2 # 🎯 只盯着它
        
        # 🌟 核心发布者：发布可视化结果图像
        # 话题名为：/camera/aruco_debug，可以在 rqt_image_view 里的下拉菜单找到
        self.viz_pub = rospy.Publisher('/camera/aruco_debug', Image, queue_size=1)
        
        # 订阅底盘主相机原始图像
        rospy.Subscriber("/camera/rgb/image_raw", Image, self.image_callback)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("👁️ ArUco 实时绿框可视化系统已启动！")
        rospy.loginfo("📡 调试图像发布话题: /camera/aruco_debug")
        rospy.loginfo("请在 PC 终端运行 [rqt_image_view] 查看画面...")
        rospy.loginfo("=======================================")

    def image_callback(self, data):
        try:
            # 将 ROS 图像消息转换为 OpenCV BGR 格式
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            rospy.logerr("CvBridge Error: %s", e)
            return

        # 视觉处理必须先转灰度图，提高速度和准确度
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 核心探测：找标签
        corners, ids, rejected = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.aruco_params)

        # 探测结果副本，准备画图
        viz_image = cv_image.copy()

        # 如果画面里有标签，并且包含我们的目标 ID 2
        if ids is not None and len(ids) > 0 and self.target_id in ids.flatten().tolist():
            # 获取 2 号标签在结果列表里的索引
            idx = ids.flatten().tolist().index(self.target_id)
            target_corner = corners[idx][0] # 提取四个角的坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            
            # 🌟 勾个帅气的绿框！
            # OpenCV 原生方法，自动画边框、方向线（蓝色那根是顶边）和 ID 数字
            aruco.drawDetectedMarkers(viz_image, [corners[idx]], np.array([[self.target_id]]))
            
            # 获取外接矩形的 X 坐标最小值和最大值，算出宽度
            min_x = np.min(target_corner[:, 0])
            max_x = np.max(target_corner[:, 0])
            box_w = int(max_x - min_x)
            
            # 标记红心准星
            center_x = int(np.mean(target_corner[:, 0]))
            center_y = int(np.mean(target_corner[:, 1]))
            cv2.circle(viz_image, (center_x, center_y), 5, (0, 0, 255), -1)
            
            # 在绿框上方写上当前测得的像素宽度，方便标定
            # 为了防止在屏幕边缘写字看不到，文字位置稍微下移一点点
            txt_y = int(np.min(target_corner[:, 1])) - 10
            if txt_y < 30: txt_y = int(np.max(target_corner[:, 1])) + 30 # 如果顶边太靠上，把字写在下面
            
            text = "W: {} px".format(box_w)
            # 画文字背景（黑色），防止背景太乱看不清字
            cv2.putText(viz_image, text, (int(min_x)+1, txt_y+1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3) # 黑色描边
            cv2.putText(viz_image, text, (int(min_x), txt_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) # 绿色主文字
            
            # 终端里稍微意思一下就行，不用刷屏
            rospy.loginfo_throttle(2.0, "🎯 识别到 2 号！当前宽度 W = 【 %d 】 px，图像已上传...", box_w)
        else:
            # 找不到目标时的 HUD 提示
            cv2.putText(viz_image, "Searching for ID 2...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

        # 🌟 最终魔法：将 OpenCV 图像重新传回 ROS 并发布
        try:
            self.viz_pub.publish(self.bridge.cv2_to_imgmsg(viz_image, "bgr8"))
        except CvBridgeError as e:
            rospy.logerr("CvBridge Publish Error: %s", e)

if __name__ == '__main__':
    try:
        ArucoVisualizer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass