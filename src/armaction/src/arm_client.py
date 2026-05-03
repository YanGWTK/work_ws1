#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import math
import actionlib
import sys
from armaction.msg import ArmControlAction, ArmControlGoal, ArmControlResult

class ArmActionClient:
    def __init__(self):
        # 创建Action客户端
        self.client = actionlib.SimpleActionClient('arm_control', ArmControlAction)
        
        # 等待服务器
        rospy.loginfo("Waiting for arm action server...")
        server_found = self.client.wait_for_server(rospy.Duration(10.0))
        
        if not server_found:
            rospy.logerr("Arm action server not found within timeout")
            sys.exit(1)
            
        rospy.loginfo("Connected to arm action server")
        
        # 预定义常用姿势
        self.poses = {
            'home': [90, 2.0, 60.0, 40.0, 90, 30],
            'jia': [90, 2.0, 60.0, 40.0, 90, 130],
            'tai': [90, 15.0, 60.0, 40.0, 90, 130],
            'stretch': [90, 145, 0, 45, 90, 30],
            'pickup': [45, 15.0, 60.0, 40.0, 90, 130],
            'fold': [45, 10.0, 60.0, 40.0, 90, 30]
        }

    def move_to_pose(self, pose_name, duration=3.0):
        """移动到预定义姿势"""
        if pose_name not in self.poses:
            rospy.logerr("Unknown pose: %s. Available: %s", pose_name, list(self.poses.keys()))
            return None
            
        return self.move_to_joints(self.poses[pose_name], duration)

    def move_to_joints(self, joints, duration=3.0, speed=1.0):
        """移动机械臂到指定关节角度"""
        # 创建目标
        goal = ArmControlGoal()
        goal.target_joints = joints
        goal.duration = duration
        goal.speed = speed
        
        rospy.loginfo("Sending goal: joints=%s, duration=%.1fs", joints, duration)
        
        # 发送目标
        self.client.send_goal(goal, feedback_cb=self.feedback_callback)
        
        # 等待结果（带超时）
        timeout = duration + 5.0  # 额外5秒容限
        success = self.client.wait_for_result(rospy.Duration(timeout))
        
        if success:
            result = self.client.get_result()
            if result.success:
                rospy.loginfo("Movement succeeded: %s", result.message)
            else:
                rospy.logwarn("Movement failed: %s", result.message)
            return result
        else:
            rospy.logerr("Movement timed out after %.1f seconds", timeout)
            self.client.cancel_goal()
            return None

    def feedback_callback(self, feedback):
        """反馈回调函数"""
        rospy.loginfo("Progress: %.1f%%, Current: %s, State: %s", 
                     feedback.progress * 100, 
                     [round(j, 1) for j in feedback.current_joints],
                     feedback.state)

    def interactive_control(self):
        """交互式控制界面"""
        rospy.loginfo("=== Arm Control Client ===")
        rospy.loginfo("Commands:")
        rospy.loginfo("  home    - 回到初始位置")
        rospy.loginfo("  stretch - 伸展姿势") 
        rospy.loginfo("  pickup  - 拾取姿势")
        rospy.loginfo("  fold    - 折叠姿势")
        rospy.loginfo("  custom  - 自定义关节角度")
        rospy.loginfo("  exit    - 退出程序")
        
        while not rospy.is_shutdown():
            try:
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'exit':
                    break
                elif command in self.poses:
                    self.move_to_pose(command, 2.0)
                elif command == 'custom':
                    self.custom_move()
                else:
                    rospy.logwarn("Unknown command: %s", command)
                    
            except EOFError:
                break
            except Exception as e:
                rospy.logerr("Command error: %s", str(e))

    def custom_move(self):
        """自定义关节角度移动"""
        try:
            rospy.loginfo("Enter target joint angles (6 values, separated by spaces):")
            user_input = input("Joints: ").strip()
            joints = [float(x) for x in user_input.split()]
            
            if len(joints) != 6:
                rospy.logerr("Need exactly 6 joint values")
                return
                
            duration = float(input("Duration (seconds): ").strip() or "3.0")
            
            self.move_to_joints(joints, duration)
            
        except ValueError as e:
            rospy.logerr("Invalid input: %s", str(e))
        except Exception as e:
            rospy.logerr("Custom move error: %s", str(e))


def main():
    rospy.init_node('arm_action_client', anonymous=True)
    
    client = ArmActionClient()
    
    # 命令行参数处理
    if len(sys.argv) > 1:
        # 命令行模式
        command = sys.argv[1]
        duration = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
        
        if command == 'home' or command == 'jia' or command == 'tai' or command == 'stretch' or command == 'pickup' or command == 'fold':
            client.move_to_pose(command, duration)
        elif command == 'custom' and len(sys.argv) > 7:
            joints = [float(x) for x in sys.argv[2:8]]
            duration = float(sys.argv[8]) if len(sys.argv) > 8 else 3.0
            client.move_to_joints(joints, duration)
        else:
            rospy.logerr("Usage: rosrun yahboomcar_bringup arm_action_client.py [pose_name|custom] [duration]")
            rospy.logerr("Poses: home, stretch, pickup, fold")
            rospy.logerr("Custom: rosrun ... arm_action_client.py custom j1 j2 j3 j4 j5 j6 [duration]")
    else:
        # 交互模式
        client.interactive_control()
    
    rospy.loginfo("Arm client shutdown.")


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
