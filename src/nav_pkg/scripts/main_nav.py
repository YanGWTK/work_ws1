#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
# 从我们刚才写的工具文件中导入函数
from nav_client import move_to_target

def main():
    # 1. 在主程序中初始化节点（整个程序生命周期只初始化这一次）
    rospy.init_node('robot_main_task_node', anonymous=True)
    
    rospy.loginfo("主控任务节点已启动...")

    # 2. 调用封装好的导航函数，传入你之前抓取到的真实坐标
    target_x = 3.0755
    target_y = 0.5145
    target_qz = -0.6753
    target_qw = 0.7374

    rospy.loginfo("准备前往第一个任务点...")
    
    # 获取函数的返回值，判断是否成功
    success = move_to_target(target_x, target_y, target_qz, target_qw)
    
    if success:
        rospy.loginfo("任务点 1 抵达，开始执行后续任务（比如播放语音、控制机械臂等）...")
        # TODO: 这里可以写到达目的地后要做的其他事情
    else:
        rospy.logwarn("未能到达任务点 1，执行备用方案或报错。")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass