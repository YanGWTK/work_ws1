#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import time
from yahboomcar_msgs.msg import ArmJoint
from std_srvs.srv import Trigger, TriggerResponse

class ArmGraspNode:
    def __init__(self):
        rospy.init_node("arm_grasp_service_node", anonymous=False)
        
        # 初始化机械臂底层直驱发布者
        self.pub_Arm = rospy.Publisher("TargetAngle", ArmJoint, queue_size=1000)
        
        # 声明抓取服务
        self.service = rospy.Service('/execute_grasp', Trigger, self.handle_grasp_request)
        self.service1 = rospy.Service('/execute_release', Trigger, self.handle_grasp_request1)

        self.standby_joints = [90.0, 180.0, 0.0, 0.0, 90.0, 30.0]
        
        rospy.loginfo("=======================================")
        rospy.loginfo("🦾 独立机械臂抓取节点已就绪！(1号舵机 95度居中)")
        rospy.loginfo("等待服务调用: rosservice call /execute_grasp")
        rospy.loginfo("=======================================")
        rospy.sleep(1.0)
        # 节点启动时，回到居中待命姿态
        self.pubArm(self.standby_joints, run_time=2000)

    def pubArm(self, joints=[], id=10, angle=90, run_time=500):
        armjoint = ArmJoint()
        armjoint.run_time = run_time
        if len(joints) != 0: 
            armjoint.joints = joints
        else:
            armjoint.id = id
            armjoint.angle = angle
        self.pub_Arm.publish(armjoint)

    def pubArm2(self, joints=[], id=10, angle=90, run_time=1000):
        armjoint = ArmJoint()
        armjoint.run_time = run_time
        if len(joints) != 0: 
            armjoint.joints = joints
        else:
            armjoint.id = id
            armjoint.angle = angle
        self.pub_Arm.publish(armjoint)
    def pubArm3(self, joints=[], id=10, angle=90, run_time=2500):
        armjoint = ArmJoint()
        armjoint.run_time = run_time
        if len(joints) != 0: 
            armjoint.joints = joints
        else:
            armjoint.id = id
            armjoint.angle = angle
        self.pub_Arm.publish(armjoint)
    def handle_grasp_request1(self, req):
        rospy.loginfo("📥 收到抓取指令！开始执行...")
        try:
            self.execute_grasp_sequence1()
            rospy.loginfo("✅ 抓取任务圆满完成！")
            res = TriggerResponse()
            res.success = True
            res.message = "Grasp execution completed."
            return res
        except Exception as e:
            rospy.logerr("🚨 抓取过程发生错误: %s", str(e))
            res = TriggerResponse()
            res.success = False
            res.message = "Grasp execution failed."
            return res
    def handle_grasp_request(self, req):
        rospy.loginfo("📥 收到抓取指令！开始执行...")
        try:
            self.execute_grasp_sequence()
            rospy.loginfo("✅ 抓取任务圆满完成！")
            res = TriggerResponse()
            res.success = True
            res.message = "Grasp execution completed."
            return res
        except Exception as e:
            rospy.logerr("🚨 抓取过程发生错误: %s", str(e))
            res = TriggerResponse()
            res.success = False
            res.message = "Grasp execution failed."
            return res
    # def execute_grasp_sequence1(self):
    #     #放置
    #     rospy.loginfo("第一步")
    #     self.pubArm([],id=2, angle=135)
    #     self.pubArm([],id=4,angle=26)
    #     rospy.loginfo("第二步")
    #     self.pubArm([],id=3,angle=35)
    #     self.pubArm([],id=5,angle=270)
    #     time.sleep(1)
    #     rospy.loginfo("第三步")             
    #     self.pubArm2([],id=3,angle=77)
    #     self.pubArm2([],id=4,angle=39)
    #     # self.pubArm2([],id=2,angle=70)
    #     time.sleep(1)        
    #     self.pubArm2([],id=2,angle=55)
    #     time.sleep(1)
    #     self.pubArm2([],id=6,angle=30)
    #     time.sleep(1)
    #     # 抓取复位
    #     self.pubArm2([],id=2,angle=70)
    #     self.pubArm2([],id=3,angle=35)
    #     self.pubArm2([],id=2,angle=100)
    #     time.sleep(1)
    #     self.pubArm2([],id=1,angle=95)
    #     self.pubArm2([],id=2,angle=125)
    #     self.pubArm2([],id=3,angle=0)
    #     self.pubArm2([],id=4,angle=0)
    #     time.sleep(1)
    def execute_grasp_sequence1(self):
        #桌子抓取放置
        rospy.loginfo("第一步")
        self.pubArm([],id=2,angle=145)
        # time.sleep(1)
        rospy.loginfo("第二步")
        self.pubArm2([],id=3,angle=40)
        self.pubArm2([],id=5,angle=270)
        # time.sleep(1)
        self.pubArm2([],id=3,angle=60) 
        # self.pubArm2([],id=2,angle=
        time.sleep(1)
        self.pubArm2([],id=4,angle=50)
        rospy.loginfo("第三步")        
        self.pubArm2([],id=2,angle=60)
        time.sleep(1)
        self.pubArm2([],id=6,angle=30)
        time.sleep(1)
        #抓取复位
        self.pubArm2([],id=2,angle=70)
        self.pubArm2([],id=2,angle=145)
        self.pubArm2([],id=3,angle=35)
        # time.sleep(1)
        self.pubArm2([],id=1,angle=90)
        self.pubArm2([],id=3,angle=0)
        self.pubArm2([],id=4,angle=0)
        # time.sleep(1)
        self.pubArm2([],id=2,angle=180)
        time.sleep(1)
    def execute_grasp_sequence(self):
        #桌子抓取
        # self.pubArm2([],id=5,angle=270)
        # self.pubArm3([],id=2,angle=90)
        # self.pubArm3([],id=4,angle=87)
        rospy.loginfo("第一步")
        self.pubArm([],id=2,angle=145)
        # time.sleep(1)
        rospy.loginfo("第二步")
        self.pubArm2([],id=3,angle=40)
        self.pubArm2([],id=5,angle=270)
        # time.sleep(1)
        self.pubArm2([],id=3,angle=60) 
        # self.pubArm2([],id=2,angle=
        time.sleep(1)
        self.pubArm2([],id=4,angle=40)
        rospy.loginfo("第三步")        
        self.pubArm2([],id=2,angle=65)
        time.sleep(1)
        self.pubArm2([],id=6,angle=140)
        time.sleep(1)
        #抓取复位
        self.pubArm2([],id=2,angle=70)
        self.pubArm2([],id=2,angle=145)
        self.pubArm2([],id=3,angle=35)
        # time.sleep(1)
        self.pubArm2([],id=1,angle=90)
        self.pubArm2([],id=3,angle=0)
        self.pubArm2([],id=4,angle=0)
        # time.sleep(1)
        self.pubArm2([],id=2,angle=180)
        time.sleep(1)

        # 1. 向下探到抓取点上方
        # rospy.loginfo("   -> 1. 探向目标点...")
        # # 【修改点 2】：下探姿态，1号舵机改为 95.0 居中死锁
        # target_joints = [95.0, 7.0, 60.0, 38.0, 90.0, 30.0]
        # self.pubArm(target_joints, run_time=3000)
        # time.sleep(2)
        
        # # 2. 微调姿态 / 张开夹爪 (6号是夹爪，2号是大臂，1号是底座)
        # rospy.loginfo("   -> 2. 调整姿态...")
        # self.pubArm([], id=6, angle=150)
        # time.sleep(0.5)
        # self.pubArm([], id=2, angle=60, run_time=1000)
        # time.sleep(1)
        
        # # 注意：这里原厂代码有个把 1号底座转到 0 度的动作。
        # # 如果你想让它就在正前方原地抓取，不要往旁边甩，这行其实可以注释掉。
        # # 我先按原厂动作保留，让你看看到底是啥效果。
        # self.pubArm([], id=1, angle=0, run_time=1000)
        # time.sleep(1)
        
        # # 3. 闭合夹爪，捏住方块
        # rospy.loginfo("   -> 3. 闭合夹爪！")
        # # 如果你想让它丢到 0 度，就保持 0.0；如果想原地抬起，这里要改成 95.0！
        # target_joints[0] = 0.0 
        # target_joints[5] = 140.0
        # self.pubArm(target_joints, run_time=1000)
        # time.sleep(1)
        
        # # 4. 抬起机械臂
        # rospy.loginfo("   -> 4. 抬起收回...")
        # self.pubArm([], id=6, angle=30)
        # time.sleep(0.5)
        # self.pubArm([], id=2, angle=90, run_time=1000)
        # time.sleep(1)
        
        # # 5. 回到待命安全姿态 (此时又会回到 95度 居中)
        # rospy.loginfo("   -> 5. 恢复待命姿态...")
        # self.pubArm(self.standby_joints, run_time=2000)
        # time.sleep(2)
    # def execute_grasp_sequence2(self):


if __name__ == '__main__':
    try:
        ArmGraspNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass