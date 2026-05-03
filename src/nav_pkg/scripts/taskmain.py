#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import actionlib
import smach
import smach_ros
from std_msgs.msg import Bool
from std_srvs.srv import Trigger, SetBool, SetBoolRequest
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

# ==========================================================
# 1. 你的专属底层导航函数
# ==========================================================
def move_to_target(x, y, qz, qw):
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.orientation.z = qz
    goal.target_pose.pose.orientation.w = qw
    rospy.loginfo("向目标发送请求：(X: %.3f, Y: %.3f)", x, y)
    client.send_goal(goal)
    wait = client.wait_for_result(rospy.Duration(60.0))
    if not wait: return False
    return client.get_state() == actionlib.GoalStatus.SUCCEEDED

class CustomNavState(smach.State):
    def __init__(self, target_x, target_y, target_qz, target_qw):
        smach.State.__init__(self, outcomes=['succeeded', 'failed'])
        self.x, self.y, self.qz, self.qw = target_x, target_y, target_qz, target_qw

    def execute(self, userdata):
        rospy.loginfo("🚥 [SMACH] 正在导航前往坐标: X={}, Y={}".format(self.x, self.y))
        return 'succeeded' if move_to_target(self.x, self.y, self.qz, self.qw) else 'failed'

# ==========================================================
# 2. 状态监听器
# ==========================================================
class WaitAlignment(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['aligned', 'failed'])
    def execute(self, userdata):
        rospy.loginfo("🚥 [SMACH] 正在等待底盘视觉进行 3D 高精度对准及突刺...")
        try:
            if rospy.wait_for_message('/align_success', Bool, timeout=60.0).data:
                return 'aligned'
            return 'failed'
        except: return 'failed'

class WaitSearch(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['found', 'failed'])
    def execute(self, userdata):
        rospy.loginfo("🚥 [SMACH] 正在等待底盘螃蟹步寻找二维码...")
        try:
            if rospy.wait_for_message('/search_success', Bool, timeout=60.0).data:
                rospy.loginfo("🚥 [SMACH] 目标已出现在视野！准备移交对齐控制权！")
                return 'found'
            return 'failed'
        except: return 'failed'

# ==========================================================
# 3. SMACH 总指挥流程配置
# ==========================================================
def main():
    rospy.init_node('ultimate_smach_controller')
    sm = smach.StateMachine(outcomes=['任务圆满完成', '任务流产'])

    with sm:
            # ==========================================================
            # 🟢 第一圈 (Y = 1.320)
            # ==========================================================
            smach.StateMachine.add('NAV_TO_PICKUP_1',
                                CustomNavState(2.048, 1.420, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_VISION_1', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_VISION_1',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_ALIGNMENT_1', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_ALIGNMENT_1', WaitAlignment(), transitions={'aligned': 'EXECUTE_GRASP_1', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_GRASP_1', 
                                smach_ros.ServiceState('/execute_grasp', Trigger), 
                                transitions={'succeeded': 'DISABLE_VISION_1', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('DISABLE_VISION_1',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'NAV_TO_DROPOFF_1', 'aborted': '任务流产', 'preempted': '任务流产'})

            smach.StateMachine.add('NAV_TO_DROPOFF_1',
                                CustomNavState(1.983, 0.366, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_SEARCH_1', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_SEARCH_1',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_SEARCH_1', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_SEARCH_1', WaitSearch(), transitions={'found': 'DISABLE_SEARCH_1', 'failed': '任务流产'})
            smach.StateMachine.add('DISABLE_SEARCH_1',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'ENABLE_DROP_ALIGN_1', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('ENABLE_DROP_ALIGN_1',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_DROP_ALIGN_1', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_DROP_ALIGN_1', WaitAlignment(), transitions={'aligned': 'EXECUTE_RELEASE_1', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_RELEASE_1', 
                                smach_ros.ServiceState('/execute_release', Trigger), 
                                transitions={'succeeded': 'DISABLE_DROP_ALIGN_1', 'aborted': '任务流产', 'preempted': '任务流产'})
            
            # 🌟 第一圈结束，导向第二圈的起点！
            smach.StateMachine.add('DISABLE_DROP_ALIGN_1',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'NAV_TO_PICKUP_2', 'aborted': '任务流产', 'preempted': '任务流产'})

            # ==========================================================
            # 🟡 第二圈 (Y = 1.081)
            # ==========================================================
            smach.StateMachine.add('NAV_TO_PICKUP_2',
                                CustomNavState(2.048, 1.181, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_VISION_2', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_VISION_2',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_ALIGNMENT_2', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_ALIGNMENT_2', WaitAlignment(), transitions={'aligned': 'EXECUTE_GRASP_2', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_GRASP_2', 
                                smach_ros.ServiceState('/execute_grasp', Trigger), 
                                transitions={'succeeded': 'DISABLE_VISION_2', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('DISABLE_VISION_2',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'NAV_TO_DROPOFF_2', 'aborted': '任务流产', 'preempted': '任务流产'})

            smach.StateMachine.add('NAV_TO_DROPOFF_2',
                                CustomNavState(1.983, 0.366, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_SEARCH_2', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_SEARCH_2',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_SEARCH_2', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_SEARCH_2', WaitSearch(), transitions={'found': 'DISABLE_SEARCH_2', 'failed': '任务流产'})
            smach.StateMachine.add('DISABLE_SEARCH_2',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'ENABLE_DROP_ALIGN_2', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('ENABLE_DROP_ALIGN_2',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_DROP_ALIGN_2', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_DROP_ALIGN_2', WaitAlignment(), transitions={'aligned': 'EXECUTE_RELEASE_2', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_RELEASE_2', 
                                smach_ros.ServiceState('/execute_release', Trigger), 
                                transitions={'succeeded': 'DISABLE_DROP_ALIGN_2', 'aborted': '任务流产', 'preempted': '任务流产'})
            
            # 🌟 第二圈结束，导向第三圈的起点！
            smach.StateMachine.add('DISABLE_DROP_ALIGN_2',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'NAV_TO_PICKUP_3', 'aborted': '任务流产', 'preempted': '任务流产'})

            # ==========================================================
            # 🔵 第三圈 (Y = 0.843)
            # ==========================================================
            smach.StateMachine.add('NAV_TO_PICKUP_3',
                                CustomNavState(2.048, 0.943, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_VISION_3', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_VISION_3',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_ALIGNMENT_3', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_ALIGNMENT_3', WaitAlignment(), transitions={'aligned': 'EXECUTE_GRASP_3', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_GRASP_3', 
                                smach_ros.ServiceState('/execute_grasp', Trigger), 
                                transitions={'succeeded': 'DISABLE_VISION_3', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('DISABLE_VISION_3',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'NAV_TO_DROPOFF_3', 'aborted': '任务流产', 'preempted': '任务流产'})

            smach.StateMachine.add('NAV_TO_DROPOFF_3',
                                CustomNavState(1.983, 0.366, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_SEARCH_3', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_SEARCH_3',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_SEARCH_3', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_SEARCH_3', WaitSearch(), transitions={'found': 'DISABLE_SEARCH_3', 'failed': '任务流产'})
            smach.StateMachine.add('DISABLE_SEARCH_3',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'ENABLE_DROP_ALIGN_3', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('ENABLE_DROP_ALIGN_3',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_DROP_ALIGN_3', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_DROP_ALIGN_3', WaitAlignment(), transitions={'aligned': 'EXECUTE_RELEASE_3', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_RELEASE_3', 
                                smach_ros.ServiceState('/execute_release', Trigger), 
                                transitions={'succeeded': 'DISABLE_DROP_ALIGN_3', 'aborted': '任务流产', 'preempted': '任务流产'})
            
            # 🌟 第三圈结束，导向第四圈的起点！
            smach.StateMachine.add('DISABLE_DROP_ALIGN_3',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'NAV_TO_PICKUP_4', 'aborted': '任务流产', 'preempted': '任务流产'})

            # ==========================================================
            # 🟣 第四圈 (Y = 0.6045)
            # ==========================================================
            smach.StateMachine.add('NAV_TO_PICKUP_4',
                                CustomNavState(2.048, 0.7045, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_VISION_4', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_VISION_4',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_ALIGNMENT_4', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_ALIGNMENT_4', WaitAlignment(), transitions={'aligned': 'EXECUTE_GRASP_4', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_GRASP_4', 
                                smach_ros.ServiceState('/execute_grasp', Trigger), 
                                transitions={'succeeded': 'DISABLE_VISION_4', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('DISABLE_VISION_4',
                                smach_ros.ServiceState('/enable_redalign', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'NAV_TO_DROPOFF_4', 'aborted': '任务流产', 'preempted': '任务流产'})

            smach.StateMachine.add('NAV_TO_DROPOFF_4',
                                CustomNavState(1.983, 0.366, 0.999, -0.03),
                                transitions={'succeeded': 'ENABLE_SEARCH_4', 'failed': '任务流产'})
            smach.StateMachine.add('ENABLE_SEARCH_4',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_SEARCH_4', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_SEARCH_4', WaitSearch(), transitions={'found': 'DISABLE_SEARCH_4', 'failed': '任务流产'})
            smach.StateMachine.add('DISABLE_SEARCH_4',
                                smach_ros.ServiceState('/enable_search', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': 'ENABLE_DROP_ALIGN_4', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('ENABLE_DROP_ALIGN_4',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(True)),
                                transitions={'succeeded': 'WAIT_DROP_ALIGN_4', 'aborted': '任务流产', 'preempted': '任务流产'})
            smach.StateMachine.add('WAIT_DROP_ALIGN_4', WaitAlignment(), transitions={'aligned': 'EXECUTE_RELEASE_4', 'failed': '任务流产'})
            smach.StateMachine.add('EXECUTE_RELEASE_4', 
                                smach_ros.ServiceState('/execute_release', Trigger), 
                                transitions={'succeeded': 'DISABLE_DROP_ALIGN_4', 'aborted': '任务流产', 'preempted': '任务流产'})
            
            # 第四圈结束
            smach.StateMachine.add('DISABLE_DROP_ALIGN_4',
                                smach_ros.ServiceState('/enable_align', SetBool, request=SetBoolRequest(False)),
                                transitions={'succeeded': '任务圆满完成', 'aborted': '任务流产', 'preempted': '任务流产'})
    rospy.loginfo("包含独立索敌接力的流水线已上线！")
    sm.execute()

if __name__ == '__main__':
    main()