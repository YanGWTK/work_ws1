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
        # 🛠️ 核心可调参数区 (调参只改这里！)
        # ==========================================
        
        # --- 速度与时间参数 ---
        self.moveit_velocity = 0.8      # MoveIt 规划的最大速度缩放因子 (0.01 ~ 1.0)
        self.moveit_acceleration = 0.5  # MoveIt 规划的最大加速度缩放因子 (0.01 ~ 1.0)
        self.direct_init_time = 2500    # 底层直驱去初始位置的时间 (毫秒)，越小越快
        self.direct_return_time = 2500  # 底层直驱抓完退回的时间 (毫秒)，越小越快
        
        # --- 空间对准偏移量 (单位：米) ---
        # 悬停点相对二维码中心的偏移：X(前后), Y(左右), Z(上下)
        self.hover_offset_x = -0.05     # 悬停在物体前方 5cm 处
        self.hover_offset_y = 0.03      # Y轴微调对准
        self.hover_offset_z = -0.01     # Z轴微调对准
        # 最终贴脸抓取点相对二维码中心的偏移：
        self.grasp_offset_x = -0.02     # 贴近到距中心 2cm 处抓取
        
        # --- 夹爪状态参数 ---
        self.gripper_open_rad = -0.1    # MoveIt 张开时的弧度值
        self.gripper_close_rad = -1.0   # MoveIt 闭合抓取时的弧度值 (越小捏得越紧)
        self.gripper_close_angle = 140.0 # 底层直驱携带物体返回时，夹爪保持闭合的角度
        
        # --- 默认姿态参数 (角度制) ---
        # [底座, 大臂, 小臂, 腕俯仰, 5号腕旋转, 夹爪]
        self.standby_joints = [90.0, 180.0, 0.0, 0.0, 270.0, 30.0]
        
        # --- 精度参数 ---
        self.goal_tolerance = 0.01      # MoveIt 目标位置容差 (米)

        # ==========================================

        # 2. 初始化底层直驱发布者
        self.pub_Arm = rospy.Publisher("TargetAngle", ArmJoint, queue_size=1000)

        # 3. 初始化 MoveIt! 控制组
        self.arm = moveit_commander.MoveGroupCommander("arm_group")
        self.gripper = moveit_commander.MoveGroupCommander("gripper_group")
        
        # 4. 配置 MoveIt 参考系与参数加载
        self.arm.set_pose_reference_frame("base_link")
        self.arm.set_goal_position_tolerance(self.goal_tolerance)
        self.arm.set_max_velocity_scaling_factor(self.moveit_velocity)
        self.arm.set_max_acceleration_scaling_factor(self.moveit_acceleration)

        # 5. TF 监听器
        self.listener = tf.TransformListener()

        rospy.loginfo("=======================================")
        rospy.loginfo("🦾 混合控制：全参数化 + 5号舵机轨迹截胡版！")
        rospy.loginfo("输入 'g' 开始抓取，输入 'q' 退出")
        rospy.loginfo("=======================================")

    def pubArmDirect(self, joints, run_time=2000):
        armjoint = ArmJoint()
        armjoint.run_time = run_time
        armjoint.joints = joints
        self.pub_Arm.publish(armjoint)
        rospy.loginfo("📢 底层直驱：发送角度序列 %s", str(joints))
        rospy.sleep(run_time / 1000.0 + 1.0)

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
        """
        🚫 核心黑魔法：轨迹截胡！
        不管 MoveIt 怎么规划，我强行把路点里的 5 号舵机数据全部焊死！
        """
        self.arm.set_position_target(target_xyz)
        plan_result = self.arm.plan()
        
        # 兼容不同版本 MoveIt 的返回值
        if isinstance(plan_result, tuple):
            success, plan, _, _ = plan_result
        else:
            success = True if plan_result.joint_trajectory.points else False
            plan = plan_result

        if not success or not plan.joint_trajectory.points:
            rospy.logerr("❌ 规划失败：无法到达 %s", str(target_xyz))
            return False

        # ✍️ 暴力篡改路线图！
        for pt in plan.joint_trajectory.points:
            pos = list(pt.positions)
            # 索引 4 对应的是 5 号舵机，全部强行覆盖为你指定的弧度
            pos[4] = locked_j5_rad  
            pt.positions = tuple(pos)

        # 执行被我们篡改过的高定版路线
        self.arm.execute(plan, wait=True)
        return True

    def execute_hybrid_grasp(self):
        # ==========================================
        # 1. 初始位姿
        # ==========================================
        rospy.loginfo("🏠 步骤 1: 角度直驱复位...")
        self.pubArmDirect(self.standby_joints, run_time=self.direct_init_time)
        
        # 等待 MoveIt 接收最新的关节状态反馈！
        rospy.sleep(1.0) 

        # ==========================================
        # 2. 视觉获取目标
        # ==========================================
        trans = self.get_marker_pose()
        if trans is None: return

        # ==========================================
        # 3. MoveIt! 视觉精准抓取 (绝对截胡锁死)
        # ==========================================
        rospy.loginfo("🎯 步骤 2: MoveIt 介入，开启轨迹截胡锁死逻辑...")
        
        # 🧠 获取当前 5 号舵机的真实弧度 (此时它物理上就是你设定的角度)
        current_joints = self.arm.get_current_joint_values()
        current_j5_rad = current_joints[4] 
        rospy.loginfo("🔒 提取 5 号舵机当前弧度: %.3f，准备强行灌入轨迹！", current_j5_rad)

        # A. 移动到二维码正前方 (应用设定的 hover 偏移量)
        hover_x = trans[0] + self.hover_offset_x
        hover_y = trans[1] + self.hover_offset_y
        hover_z = trans[2] + self.hover_offset_z
        if not self.move_hijacked([hover_x, hover_y, hover_z], current_j5_rad):
            return

        # B. 张开爪子
        gripper_goal = self.gripper.get_current_joint_values()
        gripper_goal[0] = self.gripper_open_rad 
        self.gripper.set_joint_value_target(gripper_goal)
        self.gripper.go(wait=True)

        # C. 贴脸前进 (应用设定的 grasp X 偏移量)
        if not self.move_hijacked([trans[0] + self.grasp_offset_x, hover_y, hover_z], current_j5_rad):
            return
        
        # D. 闭合爪子抓取
        gripper_goal[0] = self.gripper_close_rad 
        self.gripper.set_joint_value_target(gripper_goal)
        self.gripper.go(wait=True)
        rospy.sleep(1.0)

        # E. 原路后撤
        if not self.move_hijacked([hover_x, hover_y, hover_z], current_j5_rad):
            return

        # ==========================================
        # 4. 携物返回 
        # ==========================================
        rospy.loginfo("🏁 步骤 3: 角度直驱返回初始位...")
        capture_joints = list(self.standby_joints)
        capture_joints[5] = self.gripper_close_angle # 保持夹爪闭合
        self.pubArmDirect(capture_joints, run_time=self.direct_return_time)

        rospy.loginfo("🎉 抓取流程结束！5 号舵机绝对没有乱动过！")

if __name__ == '__main__':
    try:
        grasper = HybridGrasper()
        while not rospy.is_shutdown():
            user_input = input("\n[控制台] 输入 'g' 执行抓取，输入 'q' 退出: ").lower()
            if user_input == 'g':
                grasper.execute_hybrid_grasp()
            elif user_input == 'q':
                rospy.loginfo("退出程序...")
                break
    except rospy.ROSInterruptException:
        pass
    except KeyboardInterrupt:
        pass