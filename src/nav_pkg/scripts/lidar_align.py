#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import numpy as np
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from std_srvs.srv import SetBool, SetBoolResponse

# 依然使用你的老搭档：PID 控制器
from astra_common import simplePID

class LidarAligner:
    def __init__(self):
        rospy.init_node('lidar_align_node', anonymous=True)
        self.is_shutting_down = False
        rospy.on_shutdown(self.shutdown_hook)

        # 🌟 PID 控制器：只控制自转 (Yaw)，负责把倾斜角拧成 0 度！
        # 因为雷达精度极高，这里的 kp 可以稍微给大一点点，让车子转得更干脆
        self.pid_yaw = simplePID(kp=0.015, ki=0.0, kd=0.002)

        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        
        # SMACH 联动通信接口
        self.is_tracking_enabled = False
        self.align_done = False
        self.toggle_srv = rospy.Service('/enable_lidar_align', SetBool, self.toggle_cb)
        self.success_pub = rospy.Publisher('/align_success', Bool, queue_size=1)
        
        # 稳态锁定计时器
        self.alignment_start_time = None

        # 🌟 订阅雷达话题 (Yahboom 的雷达话题通常是 /scan)
        rospy.Subscriber("/scan", LaserScan, self.scan_callback, queue_size=1)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("📡 [工业级] 激光雷达 2D 贴边对齐节点已启动！")
        rospy.loginfo("当前状态：💤【休眠中】，等待 SMACH 唤醒...")
        rospy.loginfo("=======================================")

    def toggle_cb(self, req):
        self.is_tracking_enabled = req.data
        if self.is_tracking_enabled:
            rospy.loginfo("👁️ 收到 SMACH 唤醒指令！雷达贴边系统接管底盘！开始扫描正前方...")
            self.pid_yaw.reset()
            self.align_done = False 
            self.alignment_start_time = None
        else:
            rospy.loginfo("💤 收到 SMACH 休眠指令！交出底盘！")
            self.cmd_pub.publish(Twist())
            
        return SetBoolResponse(success=True, message="Status Changed")

    def shutdown_hook(self):
        self.is_shutting_down = True
        rospy.loginfo("🚨 接收到 Ctrl+C，正在紧急刹车...")
        for _ in range(5):
            self.cmd_pub.publish(Twist())
            rospy.sleep(0.05)

    def scan_callback(self, data):
        if not self.is_tracking_enabled or self.is_shutting_down: 
            return

        if self.align_done:
            self.success_pub.publish(True)
            self.cmd_pub.publish(Twist()) 
            rospy.loginfo_throttle(2.0, "✅ [雷达对正完毕] 正在持续向 SMACH 发送交接信号...")
            return

        twist = Twist()

        # ==========================================
        # 🛠️ 核心数学魔法 1：极坐标清洗与 ROI 截取
        # ==========================================
        ranges = np.array(data.ranges)
        # 很多雷达扫不到东西时会返回 inf 或 nan，把它们变成 0 扔掉
        ranges[np.isinf(ranges) | np.isnan(ranges)] = 0 
        
        # 计算每个点对应的物理角度 (转换为 [-pi, pi] 的标准弧度制)
        angles = data.angle_min + np.arange(len(ranges)) * data.angle_increment
        angles = (angles + np.pi) % (2 * np.pi) - np.pi 
        
        # 🌟 提取正前方 ROI：只看车头正前方 ±15 度！
        ROI_ANGLE = np.radians(15)
        
        # 🌟 第一把锁：Z 轴绝对深度隔离！只看 10cm 到 60cm 之间的物体（完美屏蔽背景墙壁）
        DIST_MIN = 0.08
        DIST_MAX = 0.3
        
        mask = (np.abs(angles) <= ROI_ANGLE) & (ranges > DIST_MIN) & (ranges < DIST_MAX)
        
        valid_ranges = ranges[mask]
        valid_angles = angles[mask]

        if len(valid_ranges) < 8:
            rospy.logwarn_throttle(1.0, "👀 正前方 60cm 内没有找到足够的纸箱面，请检查距离！")
            self.cmd_pub.publish(twist)
            self.alignment_start_time = None
            return

        # ==========================================
        # 🛠️ 核心数学魔法 2：第二把锁 - 连续性跳变检测
        # ==========================================
        # 按照角度从左到右排序
        sort_idx = np.argsort(valid_angles)
        valid_angles = valid_angles[sort_idx]
        valid_ranges = valid_ranges[sort_idx]
        
        # 检查相邻点的距离跳变
        diffs = np.abs(np.diff(valid_ranges))
        jump_indices = np.where(diffs > 0.05)[0] # 只要两个点深度差超过 5cm，就认为是扫出纸箱边缘了！
        
        if len(jump_indices) > 0:
            # 如果出现跳变，为了安全，我们只保留中间最平缓的那一段数据
            first_jump = jump_indices[0]
            valid_ranges = valid_ranges[:first_jump + 1]
            valid_angles = valid_angles[:first_jump + 1]
            
        if len(valid_ranges) < 5:
            # 切割后剩下的点太少了，放弃这一帧
            return

        # ==========================================
        # 🛠️ 核心数学魔法 3：极坐标转直角坐标 + 最小二乘法拟合
        # ==========================================
        X = valid_ranges * np.cos(valid_angles) # X 是深度（离车头有多远）
        Y = valid_ranges * np.sin(valid_angles) # Y 是横向（偏左还是偏右）
        
        # 拟合直线 X = k * Y + b。
        # 这里最精妙的是：如果纸箱跟车头绝对平行，X 应该全是一样的，此时斜率 k 必须等于 0！
        k, b = np.polyfit(Y, X, 1)
        
        # 把斜率还原成倾斜角度 (Degree)
        angle_error_deg = np.degrees(np.arctan(k))
        
        # 计算纸箱正中心的平均距离 (用来做防撞或判断远近)
        center_distance = np.mean(X)

        # ==========================================
        # 🏁 最终判决：PID 纠偏与 2 秒稳态考察
        # ==========================================
        # 🌟 容忍度：雷达极其精准，我们要求它必须对正到 1.5 度以内！
        TOLERANCE_DEG = 1.5 
        
        if abs(angle_error_deg) > TOLERANCE_DEG:
            # 误差太大，打断计时器，疯狂输出 PID 控制自转！
            if self.alignment_start_time is not None:
                self.alignment_start_time = None
                rospy.logwarn("⚠️ [姿态漂移] 对齐被打破，重新调整...")
            
            # 计算角速度：注意正负号，可能需要根据你小车的转向极性加个负号
            vel_z = self.pid_yaw.compute(0, angle_error_deg) 
            
            # 限制最高转速，防止甩尾太猛
            twist.angular.z = max(min(vel_z, 0.3), -0.3) 
            
            rospy.loginfo_throttle(0.2, "-> [扭转中] 当前夹角误差: %5.2f° | 平均距离: %.2fm", angle_error_deg, center_distance)
            self.cmd_pub.publish(twist)
            
        else:
            # 🎯 夹角已经小于 1.5 度！车身已经绝对平行于纸箱！
            twist.angular.z = 0.0
            self.cmd_pub.publish(twist)
            
            if self.alignment_start_time is None:
                self.alignment_start_time = rospy.Time.now()
                rospy.loginfo("🎯 [初次对准] 雷达拟合夹角: %.2f°！开启 2 秒死区考察期...", angle_error_deg)
            else:
                elapsed_time = (rospy.Time.now() - self.alignment_start_time).to_sec()
                if elapsed_time >= 2.0:
                    rospy.loginfo("==================================================")
                    rospy.loginfo("🏆 [终极锁定] 雷达数学级物理贴边成功！误差: %.2f°", angle_error_deg)
                    rospy.loginfo("==================================================")
                    self.align_done = True
                else:
                    rospy.loginfo_throttle(0.5, "⏳ 稳态锁定中... 剩余 {:.1f} 秒".format(2.0 - elapsed_time))

if __name__ == '__main__':
    try:
        LidarAligner()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass