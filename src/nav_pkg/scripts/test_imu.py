#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import math
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

def odom_callback(msg):
    # 1. 从 /odom 消息中提取四元数 (x, y, z, w)
    orientation_q = msg.pose.pose.orientation
    orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
    
    # 2. 调用 tf 库将四元数转换成欧拉角 (返回弧度: Roll, Pitch, Yaw)
    (roll, pitch, yaw) = euler_from_quaternion(orientation_list)
    
    # 3. 把弧度 (Radian) 转换成角度 (Degree)
    yaw_degree = math.degrees(yaw)
    
    # 优化点：使用 loginfo_throttle 限制打印频率，每 0.5 秒打印一次，防止终端疯狂刷屏
    rospy.loginfo_throttle(0.5, "车头朝向 (Yaw) -> 弧度: %.3f rad | 角度: %.1f°", yaw, yaw_degree)

if __name__ == '__main__':
    try:
        rospy.init_node('get_yaw_node', anonymous=True)
        
        # 订阅小车的里程计话题
        rospy.Subscriber('/odom', Odometry, odom_callback)
        
        rospy.loginfo("🧭 Yaw角监听器已启动！请试着用手转动一下小车... (数据每0.5秒刷新)")
        rospy.spin()
        
    except rospy.ROSInterruptException:
        # 优化点：优雅地处理 Ctrl+C 退出，避免抛出红字报错
        rospy.loginfo("监听器已安全退出。")