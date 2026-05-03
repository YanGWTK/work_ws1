#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import sys
import tf
import time
import moveit_commander
from yahboomcar_msgs.msg import ArmJoint 
from geometry_msgs.msg import Pose

class HybridGrasper:
    def __init__(self):
        # 1. 初始化 MoveIt! 与 ROS 节点
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('hybrid_grasp_node', anonymous=True)

        # ==========================================
        # 🛠️ 核心可调参数区
        # ==========================================
        
        self.moveit_velocity = 0.8      
        self.moveit_acceleration = 0.5  
        self.direct_init_time = 2500    
        self.direct_return_time = 2500  
        
        # 🌟 夹爪抓取时间与稳定时间
        self.gripper_action_time = 1500 # 夹爪闭合动作的执行时间(毫秒)
        self.grasp_stable_time = 1.5    # 闭合后，额外等待的稳定时间(秒)
        
        # --- 空间对准偏移量 (单位：米) ---
        self.hover_offset_x = 0.02     # 悬停在物体前方 5cm 处
        self.hover_offset_y = 0.03      
        self.hover_offset_z = -0.01     
        self.grasp_offset_x = 0.02     # 贴脸抓取点
        
        # --- 夹爪物理角度参数 (底层直驱使用) ---
        self.gripper_open_angle = 30.0   # 物理夹爪张开的角度
        self.gripper_close_angle = 110.0 # 物理夹爪闭合的角度 (捏紧物体)
        
        # --- 默认姿态参数 (角度制) ---
        self.standby_joints = [90.0, 180.0, 0.0, 0.0, 270.0, self.gripper_open_angle]
        self.goal_tolerance = 0.01      

        # ==========================================

        # 2. 初始化底层直驱发布者
        self.pub_Arm = rospy.Publisher("TargetAngle", ArmJoint, queue_size=1000)

        # 3. 初始化 MoveIt! 控制组 (不用 gripper_group)
        self.arm = moveit_commander.MoveGroupCommander("arm_group")
        
        # 4. 配置 MoveIt 参考系
        self.arm.set_pose_reference_frame("base_link")
        self.arm.set_goal_position_tolerance(self.goal_tolerance)
        self.arm.set_max_velocity_scaling_factor(self.moveit_velocity)
        self.arm.set_max_acceleration_scaling_factor(self.moveit_acceleration)

        # 5. TF 监听器
        self.listener = tf.TransformListener()

        rospy.loginfo("=======================================")
        rospy.loginfo("🦾 稳抓稳打版：单舵机独立控制 + 抓稳后直接捞取！")
        rospy.loginfo("输入 'g' 开始抓取，输入 'q' 退出")
        rospy.loginfo("=======================================")

    def pubArmDirect(self, joints, run_time=2000):
        """控制全臂 6 个舵机"""
        armjoint = ArmJoint()
        armjoint.run_time = run_time
        armjoint.joints = joints
        self.pub_Arm.publish(armjoint)
        rospy.loginfo("📢 全臂直驱：发送角度序列 %s", [round(j, 1) for j in joints])
        rospy.sleep(run_time / 1000.0 + 0.5)

    def pubSingleJoint(self, servo_id, target_angle, run_time=1000):
        """
        🦞 核心绝招：单舵机独立控制！
        只给指定的 ID 发送角度，joints 数组留空。底层板子会自动保持其他舵机不动！
        """
        armjoint = ArmJoint()
        armjoint.id = servo_id       # 指定舵机 ID (夹爪是 6)
        armjoint.angle = target_angle # 指定角度
        armjoint.run_time = run_time
        armjoint.joints = []         # 留空，防止干涉大臂
        
        self.pub_Arm.publish(armjoint)
        rospy.loginfo("🦞 独立直驱：舵机 ID:%d 移动到 %.1f°", servo_id, target_angle)
        rospy.sleep(run_time / 1000.0) # 等待机械动作完成

    def get_marker_pose(self):
        rospy.loginfo("👀 正在搜索二维码...")
        try:
            self.listener.waitForTransform('base_link', 'aruco_marker_frame', rospy.Time(0), rospy.Duration(3.0))
            (trans, rot) = self.listener.lookupTransform('base_link', 'aruco_marker_frame', rospy.Time(0))
            rospy.loginfo("🎯 锁定目标：X:%.3f, Y:%.3f, Z:%.3f", trans[0], trans[1], trans[2])
            return trans
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.logerr("❌ 视觉丢失：请确认二维码是否在相机范围内")
            return None

    def move_hijacked(self, target_xyz, locked_j5_rad):
        """轨迹截胡法"""
        self.arm.set_position_target(target_xyz)
        plan_result = self.arm.plan()
        
        if isinstance(plan_result, tuple):
            success, plan, _, _ = plan_result
        else:
            success = True if plan_result.joint_trajectory.points else False
            plan = plan_result

        if not success or not plan.joint_trajectory.points:
            rospy.logerr("❌ 规划失败：无法到达 %s", [round(v, 3) for v in target_xyz])
            return False

        for pt in plan.joint_trajectory.points:
            pos = list(pt.positions)
            pos[4] = locked_j5_rad  
            pt.positions = tuple(pos)

        self.arm.execute(plan, wait=True)
        return True

    def execute_hybrid_grasp(self):
        # 1. 初始位姿
        rospy.loginfo("🏠 步骤 1: 全臂复位，进入待命姿态...")
        self.pubArmDirect(self.standby_joints, run_time=self.direct_init_time)
        rospy.sleep(1.0) 

        # 2. 视觉获取目标
        trans = self.get_marker_pose()
        if trans is None: return

        # 3. 提取 5 号舵机当前弧度用于截胡
        current_j5_rad = self.arm.get_current_joint_values()[4] 

        # ==========================================
        # 4. 执行车间级流水线抓取
        # ==========================================
        rospy.loginfo("🎯 步骤 2: 开始执行平推抓取...")

        # A. 移动到悬停点
        hover_x = trans[0] + self.hover_offset_x
        hover_y = trans[1] + self.hover_offset_y
        hover_z = trans[2] + self.hover_offset_z
        rospy.loginfo("▶️ A. 前往悬停点...")
        if not self.move_hijacked([hover_x, hover_y, hover_z], current_j5_rad): return

        # B. 原地独立张开夹爪 (单控 6 号舵机)
        rospy.loginfo("▶️ B. 张开夹爪准备...")
        self.pubSingleJoint(6, self.gripper_open_angle, run_time=1000)

        # C. 贴脸前进到抓取点
        rospy.loginfo("▶️ C. 贴近目标...")
        if not self.move_hijacked([trans[0] + self.grasp_offset_x, hover_y, hover_z], current_j5_rad): return
        
        # D. 原地独立闭合夹爪，并等待稳定！！！
        rospy.loginfo("▶️ D. 闭合夹爪进行抓取...")
        self.pubSingleJoint(6, self.gripper_close_angle, run_time=self.gripper_action_time)
        
        rospy.loginfo("⏳ 等待 %.1f 秒，确保夹爪咬合力度稳定...", self.grasp_stable_time)
        rospy.sleep(self.grasp_stable_time) # 👈 核心：稳定抓取期

        # ==========================================
        # 5. 携物返回 (直接捞取！)
        # ==========================================
        # 移除了 MoveIt 的原路后撤，直接连贯抬起！
        rospy.loginfo("🏁 步骤 3: 抓取完毕！直接连贯捞取返回待命姿态...")
        capture_joints = list(self.standby_joints)
        capture_joints[5] = self.gripper_close_angle # 保持夹爪死死捏紧
        self.pubArmDirect(capture_joints, run_time=self.direct_return_time)

        rospy.loginfo("🎉 完美捞取流程结束！")

if __name__ == '__main__':
    try:
        grasper = HybridGrasper()
        while not rospy.is_shutdown():
            user_input = input("\n[控制台] 输入 'g' 开始抓取，输入 'q' 退出: ").lower()
            if user_input == 'g':
                grasper.execute_hybrid_grasp()
            elif user_input == 'q':
                rospy.loginfo("退出程序...")
                break
    except rospy.ROSInterruptException:
        pass
    except KeyboardInterrupt:
        pass