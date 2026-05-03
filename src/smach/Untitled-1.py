#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import smach
import smach_ros

# 1. 定义导航到客厅的状态
class NavToLivingRoom(smach.State):
    def __init__(self):
        # outcomes: 定义这个状态执行完可能的结果
        smach.State.__init__(self, outcomes=['reached', 'failed'])

    def execute(self, userdata):
        rospy.loginfo('正在导航至客厅...')
        # 这里应该添加调用 move_base Action Client 的代码
        # 假设导航成功：
        rospy.sleep(2) # 模拟执行时间
        return 'reached'

# 2. 定义视觉识别状态 (注意 userdata 的使用)
class FindObject(smach.State):
    def __init__(self):
        # output_keys: 定义要传递给下一个状态的数据变量名
        smach.State.__init__(self, 
                             outcomes=['found', 'not_found'],
                             output_keys=['target_pose_out'])

    def execute(self, userdata):
        rospy.loginfo('正在开启 RGB-D 摄像头识别目标...')
        # 这里应该添加调用 YOLO 和处理深度图、TF变换的代码
        # 假设识别成功，将获取到的 3D 坐标写入 userdata
        rospy.sleep(2)
        userdata.target_pose_out = {'x': 1.2, 'y': 0.0, 'z': 0.8} # 模拟 3D 坐标
        rospy.loginfo('找到目标物体！')
        return 'found'

# 3. 定义机械臂抓取状态
class GraspObject(smach.State):
    def __init__(self):
        # input_keys: 声明需要从上一个状态接收的数据
        smach.State.__init__(self, 
                             outcomes=['grasped', 'grasp_failed'],
                             input_keys=['target_pose_in'])

    def execute(self, userdata):
        rospy.loginfo('准备抓取物体...')
        # 从 userdata 中提取上一步传过来的坐标
        target = userdata.target_pose_in
        rospy.loginfo(f'接收到目标坐标: x={target["x"]}, y={target["y"]}, z={target["z"]}')
        
        # 这里添加调用 MoveIt! 执行抓取的代码
        rospy.sleep(2)
        return 'grasped'

# 4. 定义导航到卧室的状态
class NavToBedroom(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['reached', 'failed'])

    def execute(self, userdata):
        rospy.loginfo('抓取成功，正在导航至卧室...')
        rospy.sleep(2)
        return 'reached'

# 5. 定义放置物体的状态
class PlaceObject(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['placed', 'place_failed'])

    def execute(self, userdata):
        rospy.loginfo('正在将物体放置在指定位置...')
        rospy.sleep(2)
        return 'placed'

# 主函数：组装状态机
def main():
    rospy.init_node('smach_task_controller')

    # 创建一个顶级状态机，定义最终任务的结局
    sm = smach.StateMachine(outcomes=['MISSION_COMPLETED', 'MISSION_FAILED'])

    # 打开状态机容器开始添加状态
    with sm:
        # 添加状态，并定义状态之间的跳转关系
        smach.StateMachine.add('NAV_TO_LIVING_ROOM', NavToLivingRoom(), 
                               transitions={'reached':'FIND_OBJECT', 
                                            'failed':'MISSION_FAILED'})

        # 注意：这里的 remapping 将 FindObject 输出的 key 映射到状态机的全局变量
        smach.StateMachine.add('FIND_OBJECT', FindObject(), 
                               transitions={'found':'GRASP_OBJECT', 
                                            'not_found':'MISSION_FAILED'},
                               remapping={'target_pose_out':'sm_target_pose'})

        # 接收全局变量 sm_target_pose 作为输入
        smach.StateMachine.add('GRASP_OBJECT', GraspObject(), 
                               transitions={'grasped':'NAV_TO_BEDROOM', 
                                            'grasp_failed':'MISSION_FAILED'},
                               remapping={'target_pose_in':'sm_target_pose'})

        smach.StateMachine.add('NAV_TO_BEDROOM', NavToBedroom(), 
                               transitions={'reached':'PLACE_OBJECT', 
                                            'failed':'MISSION_FAILED'})

        smach.StateMachine.add('PLACE_OBJECT', PlaceObject(), 
                               transitions={'placed':'MISSION_COMPLETED', 
                                            'place_failed':'MISSION_FAILED'})

    # 创建并启动 SMACH 内部监视服务器 (非常重要：用于可视化)
    sis = smach_ros.IntrospectionServer('home_robot_smach', sm, '/SM_ROOT')
    sis.start()

    # 执行状态机
    rospy.loginfo('开始执行家庭服务任务状态机...')
    outcome = sm.execute()
    rospy.loginfo(f'任务最终结果: {outcome}')

    # 等待 ROS 节点退出
    rospy.spin()
    sis.stop()

if __name__ == '__main__':
    main()