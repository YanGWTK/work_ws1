#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import math
import threading
import actionlib
from math import pi
from time import sleep
from collections import deque
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import time


# 导入自定义Action消息（编译后自动生成）
from armaction.msg import ArmControlAction, ArmControlFeedback, ArmControlResult

# 导入硬件控制库
try:
    from Rosmaster_Lib import Rosmaster
except ImportError:
    # 模拟模式
    class Rosmaster:
        def __init__(self): 
            self.connected = False
        def set_uart_servo_angle_array(self, angles, run_time): 
            rospy.loginfo(f"Simulated arm move to {angles} in {run_time}ms")
        def get_uart_servo_angle_array(self): 
            # 模拟偶尔返回无效值
            import random
            if random.random() < 0.3:  # 30%概率返回无效值
                return [-1, -1, -1, -1, -1, -1]
            return [90, 90, 90, 90, 90, 180]
        def create_receive_threading(self): 
            rospy.loginfo("Simulated receive threading started")
        def set_beep(self, state): 
            rospy.loginfo(f"Simulated beep: {'ON' if state else 'OFF'}")


class RobustArmActionServer:
    def __init__(self):
        rospy.init_node('arm_action_server', anonymous=True)
        
        # 硬件初始化
        self.car = Rosmaster()
        self.car.create_receive_threading()
        
        # 机械臂参数
        self.joint_names = ['arm_joint1', 'arm_joint2', 'arm_joint3', 
                          'arm_joint4', 'arm_joint5', 'arm_joint6']
        
        # 关节限位
        self.joint_limits = [
            (0, 180),    # 关节1
            (0, 180),    # 关节2  
            (0, 180),    # 关节3
            (0, 180),    # 关节4
            (0, 270),    # 关节5
            (0, 180)     # 关节6
        ]
        
        # 状态管理
        self.current_joints = [90.0] * 6  # 当前关节角度
        self.last_valid_joints = [90.0] * 6  # 上一次有效的关节角度
        self.joint_valid = [True] * 6  # 每个关节是否有效
        self.is_moving = False
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
        # 数据滤波
        self.angle_history = deque(maxlen=5)  # 保存最近5次有效读数
        
        # Action服务器
        self.server = actionlib.SimpleActionServer(
            'arm_control', 
            ArmControlAction, 
            execute_cb=self.execute_callback,
            auto_start=False
        )
        self.server.start()
        
        # 关节状态发布器
        self.joint_state_pub = rospy.Publisher('/joint_states', JointState, queue_size=10)
        
        # 启动关节状态发布线程
        self.joint_pub_thread = threading.Thread(target=self.publish_joint_states_robust)
        self.joint_pub_thread.daemon = True
        self.joint_pub_thread.start()
        
        rospy.loginfo("Robust Arm Action Server initialized - 负数不会停止运行!")
        rospy.loginfo("关节名称: %s", self.joint_names)
        
        # 蜂鸣器提示
        self.car.set_beep(1)
        time.sleep(0.1)
        self.car.set_beep(0)

    def is_valid_angle(self, angle, joint_index):
        """检查角度是否有效"""
        if angle is None:
            return False
            
        # 转换为浮点数
        try:
            angle_float = float(angle)
        except (ValueError, TypeError):
            return False
        
        # 基本范围检查（比实际限位宽松）
        lower, upper = self.joint_limits[joint_index]
        expanded_lower = lower - 10  # 允许10度负偏差
        expanded_upper = upper + 10  # 允许10度正偏差
        
        if angle_float < expanded_lower or angle_float > expanded_upper:
            return False
            
        return True

    def validate_and_filter_angles(self, raw_angles):
        """验证和过滤关节角度，处理无效值"""
        if not raw_angles or len(raw_angles) != 6:
            rospy.logwarn("无效的关节角度数据: %s", raw_angles)
            return None, 0  # 返回None和错误计数
            
        validated_angles = []
        valid_count = 0
        
        for i, angle in enumerate(raw_angles):
            if self.is_valid_angle(angle, i):
                validated_angles.append(float(angle))
                valid_count += 1
                self.joint_valid[i] = True
            else:
                # 使用上一次的有效值
                rospy.logdebug("关节%d角度无效: %.1f, 使用上一次的有效值: %.1f", 
                              i+1, angle, self.last_valid_joints[i])
                validated_angles.append(self.last_valid_joints[i])
                self.joint_valid[i] = False
                
        # 如果所有关节都无效，则完全使用上一次的值
        if valid_count == 0:
            rospy.logwarn("所有关节角度无效，完全使用上一次的值")
            return self.last_valid_joints.copy(), 0
            
        return validated_angles, 6 - valid_count  # 返回处理后的角度和无效计数

    def apply_low_pass_filter(self, new_angles):
        """应用低通滤波器平滑数据"""
        if not new_angles:
            return self.current_joints
            
        # 添加新读数到历史
        self.angle_history.append(new_angles)
        
        # 如果历史数据太少，直接返回新值
        if len(self.angle_history) < 2:
            return new_angles
        
        # 加权移动平均滤波（最近的权重更高）
        filtered = []
        history_list = list(self.angle_history)
        
        for i in range(6):
            weights = []
            values = []
            
            # 为每个历史点分配权重（越近权重越高）
            for j, hist in enumerate(history_list):
                if i < len(hist):
                    weight = (j + 1) / len(history_list)  # 线性权重
                    weights.append(weight)
                    values.append(hist[i])
            
            if values:
                # 计算加权平均
                total_weight = sum(weights)
                weighted_sum = sum(v * w for v, w in zip(values, weights))
                filtered.append(weighted_sum / total_weight)
            else:
                filtered.append(self.current_joints[i])  # 使用当前值
                
        return filtered

    def publish_joint_states_robust(self):
        """稳健的关节状态发布 - 处理无效值不会停止"""
        rate = rospy.Rate(20)  # 降低到20Hz，提高稳定性
        
        error_count = 0
        max_errors_before_warning = 5
        
        while not rospy.is_shutdown():
            try:
                # 1. 从硬件读取原始数据
                raw_angles = self.car.get_uart_servo_angle_array()
                
                # 2. 验证和过滤数据
                validated_angles, invalid_count = self.validate_and_filter_angles(raw_angles)
                
                if validated_angles is None:
                    error_count += 1
                    rospy.logdebug("无法获取有效的关节角度，错误计数: %d", error_count)
                    
                    if error_count >= max_errors_before_warning:
                        rospy.logwarn("连续%d次读取失败，但继续运行...", error_count)
                    
                    # 即使读取失败，也发布上一次的有效值保持系统运行
                    validated_angles = self.last_valid_joints.copy()
                else:
                    # 更新上一次的有效值
                    self.last_valid_joints = validated_angles.copy()
                    error_count = 0  # 重置错误计数
                
                # 3. 应用滤波
                filtered_angles = self.apply_low_pass_filter(validated_angles)
                
                # 4. 更新当前状态
                self.current_joints = filtered_angles
                
                # 5. 发布关节状态（即使有无效值也继续发布）
                self.publish_joint_state_message(filtered_angles)
                
                # 6. 定期报告状态
                if rospy.get_time() % 10 < 0.1:  # 每10秒报告一次
                    invalid_joints = [i+1 for i, valid in enumerate(self.joint_valid) if not valid]
                    if invalid_joints:
                        rospy.logwarn("以下关节读取不稳定: %s", invalid_joints)
                    else:
                        rospy.loginfo("所有关节读取正常")
                
            except Exception as e:
                error_count += 1
                rospy.logwarn("关节状态发布错误 (计数: %d): %s", error_count, str(e))
                
                # 即使出错也继续发布上一次的值
                self.publish_joint_state_message(self.last_valid_joints)
            
            rate.sleep()

    def publish_joint_state_message(self, angles):
        """发布关节状态消息"""
        try:
            joint_state = JointState()
            joint_state.header = Header()
            joint_state.header.stamp = rospy.Time.now()
            joint_state.name = self.joint_names
            
            # 转换为弧度
            joint_state.position = [angle * pi / 180.0 for angle in angles]
            
            self.joint_state_pub.publish(joint_state)
            
        except Exception as e:
            rospy.logwarn("创建关节状态消息失败: %s", str(e))

    def check_joint_limits(self, target_joints):
        """检查关节限位 - 宽松版本"""
        if len(target_joints) != 6:
            return False, "需要6个关节角度值"
        
        for i, angle in enumerate(target_joints):
            lower, upper = self.joint_limits[i]
            if angle < lower or angle > upper:
                return False, "关节{}角度{:.1f}超出限制[{}, {}]".format(i+1, angle, lower, upper)
        
        return True, "角度检查通过"

    def execute_callback(self, goal):
        """Action执行回调 - 处理无效值不会停止运动"""
        rospy.loginfo("收到新的机械臂目标: %s", goal.target_joints)
        
        # 标记开始运动
        self.is_moving = True
        self.consecutive_errors = 0
        
        try:
            # 1. 目标验证
            is_valid, message = self.check_joint_limits(goal.target_joints)
            if not is_valid:
                result = ArmControlResult()
                result.success = False
                result.message = "目标无效: " + message
                self.server.set_aborted(result)
                self.is_moving = False
                return

            # 2. 运动参数
            duration = max(0.5, goal.duration)  # 最小0.5秒
            start_joints = self.current_joints.copy()
            target_joints = goal.target_joints
            
            rospy.loginfo("从 %s 移动到 %s, 用时 %.1f 秒", start_joints, target_joints, duration)
            
            start_time = rospy.Time.now()
            rate = rospy.Rate(30)  # 30Hz控制频率
            
            # 3. 运动执行循环
            while not rospy.is_shutdown() and self.is_moving:
                # 检查是否被取消
                if self.server.is_preempt_requested():
                    rospy.loginfo("机械臂运动被用户取消")
                    result = ArmControlResult()
                    result.success = False
                    result.message = "运动被用户取消"
                    self.server.set_preempted(result)
                    self.is_moving = False
                    return
                
                # 计算当前进度 (0-1)
                elapsed = (rospy.Time.now() - start_time).to_sec()
                progress = min(elapsed / duration, 1.0)
                
                # 轨迹插值（线性插值）
                current_target = []
                for i in range(6):
                    start_angle = start_joints[i]
                    target_angle = target_joints[i]
                    current_angle = start_angle + (target_angle - start_angle) * progress
                    current_target.append(current_angle)
                
                # 发送到硬件
                run_time = 20  # 固定20ms
                try:
                    self.car.set_uart_servo_angle_array(current_target, run_time)
                    self.consecutive_errors = 0  # 重置错误计数
                except Exception as e:
                    self.consecutive_errors += 1
                    rospy.logwarn("发送命令到硬件失败 (错误计数: %d): %s", 
                                 self.consecutive_errors, str(e))
                    
                    # 即使发送失败也继续运动，不停止
                    if self.consecutive_errors >= 5:
                        rospy.logwarn("连续发送失败，但继续尝试...")
                
                # 发布反馈 - 使用当前关节角度（可能包含滤波后的值）
                feedback = ArmControlFeedback()
                feedback.current_joints = self.current_joints
                feedback.progress = progress
                
                # 添加状态信息
                invalid_count = sum(1 for valid in self.joint_valid if not valid)
                if invalid_count > 0:
                    feedback.state = "运动中 ({}个关节读数不稳定)".format(invalid_count)
                else:
                    feedback.state = "移动到目标" if progress < 1.0 else "目标已到达"
                
                # 只在服务器活跃时发布反馈
                if self.server.is_active():
                    self.server.publish_feedback(feedback)
                
                # 检查是否完成
                if progress >= 1.0:
                    rospy.loginfo("机械臂运动完成")
                    break
                
                rate.sleep()
            
            # 4. 运动完成，等待稳定
            rospy.sleep(0.5)  # 额外等待0.5秒稳定
            
            # 5. 验证最终位置（宽松验证）
            final_error = self.calculate_position_error(target_joints, self.current_joints)
            success = final_error < 10.0  # 放宽误差阈值到10度
            
            # 6. 设置结果
            result = ArmControlResult()
            result.success = success
            
            # 添加详细信息
            invalid_joints = [i+1 for i, valid in enumerate(self.joint_valid) if not valid]
            if invalid_joints:
                result.message = "运动完成，但关节{}读数不稳定，最终误差: {:.1f}度".format(
                    invalid_joints, final_error)
            else:
                result.message = "机械臂运动完成，最终误差: {:.1f}度".format(final_error)
            
            if success:
                self.server.set_succeeded(result)
                rospy.loginfo("机械臂动作成功: %s", result.message)
            else:
                self.server.set_aborted(result)
                rospy.logwarn("机械臂动作完成但有警告: %s", result.message)
            
        except Exception as e:
            rospy.logerr("机械臂动作执行失败: %s", str(e))
            result = ArmControlResult()
            result.success = False
            result.message = "执行错误: " + str(e)
            self.server.set_aborted(result)
        
        finally:
            self.is_moving = False

    def calculate_position_error(self, target, actual):
        """计算位置误差"""
        if len(target) != 6 or len(actual) != 6:
            return float('inf')
        
        error = 0.0
        valid_joints = 0
        
        for i in range(6):
            if self.joint_valid[i]:  # 只计算有效关节的误差
                error += abs(target[i] - actual[i])
                valid_joints += 1
        
        if valid_joints == 0:
            return float('inf')
            
        return error / valid_joints  # 平均误差（只计算有效关节）

    def run(self):
        """主运行循环"""
        rospy.loginfo("稳健机械臂服务器运行中...")
        rospy.loginfo("特性:")
        rospy.loginfo("  - 读取到负数不会停止运行")
        rospy.loginfo("  - 使用上一次有效值替代无效值")
        rospy.loginfo("  - 应用滤波平滑数据")
        rospy.loginfo("  - 宽松的错误处理")
        
        # 注册关闭回调
        rospy.on_shutdown(self.shutdown_handler)
        
        try:
            rospy.spin()
        except KeyboardInterrupt:
            rospy.loginfo("用户关闭机械臂服务器")

    def shutdown_handler(self):
        """关闭时的清理工作"""
        rospy.loginfo("关闭稳健机械臂服务器...")
        self.is_moving = False
        
        # 蜂鸣器提示
        self.car.set_beep(1)
        time.sleep(0.1)
        self.car.set_beep(0)
        time.sleep(0.1)
        self.car.set_beep(1)
        time.sleep(0.1)
        self.car.set_beep(0)


if __name__ == '__main__':
    try:
        server = RobustArmActionServer()
        server.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("机械臂服务器完成.")
    except Exception as e:
        rospy.logerr("启动机械臂服务器失败: %s", str(e))
