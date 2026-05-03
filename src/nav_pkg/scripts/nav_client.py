#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

def move_to_target(x, y, qz, qw):
    """
    控制机器人移动到指定目标点。
    注意：调用此函数前，调用者必须已经执行了 rospy.init_node()。
    
    参数:
        x (float): 目标点 X 坐标
        y (float): 目标点 Y 坐标
        qz (float): 目标朝向四元数的 Z 值
        qw (float): 目标朝向四元数的 W 值
        
    返回:
        bool: 成功到达返回 True，否则返回 False
    """
    # 创建 Action 客户端
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    
    rospy.loginfo("等待 move_base 服务器响应...")
    client.wait_for_server()

    # 创建目标点对象
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    
    # 填入传入的参数
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.position.z = 0.0
    
    goal.target_pose.pose.orientation.x = 0.0
    goal.target_pose.pose.orientation.y = 0.0
    goal.target_pose.pose.orientation.z = qz
    goal.target_pose.pose.orientation.w = qw

    rospy.loginfo("向目标发送请求：(X: %.3f, Y: %.3f)", x, y)
    client.send_goal(goal)

    # 等待结果（超时设置可以根据你的 Yahboom 机器人的实际移动速度来调整，这里暂设 60 秒）
    wait = client.wait_for_result(rospy.Duration(60.0))
    
    if not wait:
        rospy.logerr("导航超时！取消任务。")
        client.cancel_goal()
        return False
    else:
        state = client.get_state()
        if state == actionlib.GoalStatus.SUCCEEDED:
            rospy.loginfo("成功到达目标点！")
            return True
        else:
            rospy.logerr("导航失败，状态码: %s", str(state))
            return False