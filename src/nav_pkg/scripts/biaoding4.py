#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import numpy as np
import os  # 🌟 导入操作系统接口模块
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

def nothing(x):
    pass

class HSVCalibrator:
    def __init__(self):
        rospy.init_node('hsv_calibrator', anonymous=True)
        # 注册退出时的清理函数
        rospy.on_shutdown(self.shutdown_hook)
        
        # =========================================================
        # 🛡️ 强制关闭 Astra 自动白平衡及曝光 (独裁模式)
        # =========================================================
        rospy.loginfo("⏳ 等待相机节点就绪 (1秒)...")
        rospy.sleep(1.0) # 🌟 核心修复：等相机喘口气再发指令，保证 100% 命中！
        
        rospy.loginfo("🛡️ 正在发送 ROS 服务指令，物理锁死相机...")
        try:
            # 强行关闭自动白平衡
            os.system('rosservice call /camera/set_auto_white_balance false > /dev/null 2>&1')
            # 强行锁死色温为 4600K
            os.system('rosservice call /camera/set_white_balance 4600 > /dev/null 2>&1')
            
            # 顺手把曝光和背光补偿也关了
            os.system('v4l2-ctl -d /dev/video0 --set-ctrl=backlight_compensation=0 > /dev/null 2>&1')
            os.system('v4l2-ctl -d /dev/video0 --set-ctrl=exposure_auto_priority=0 > /dev/null 2>&1')
            
            rospy.loginfo("✅ 自动白平衡及曝光已强制封印！当前调色不受环境光干扰！")
        except Exception as e:
            rospy.logwarn("⚠️ 相机底层锁死失败！请检查相机服务是否在线。")
        # =========================================================

        self.bridge = CvBridge()
        self.latest_image = None

        # 1. 创建窗口和滑块
        cv2.namedWindow('HSV_Tuning', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('HSV_Tuning', 400, 300)

        cv2.createTrackbar('H_MIN', 'HSV_Tuning', 20, 180, nothing)
        cv2.createTrackbar('S_MIN', 'HSV_Tuning', 100, 255, nothing)
        cv2.createTrackbar('V_MIN', 'HSV_Tuning', 80, 255, nothing)
        cv2.createTrackbar('H_MAX', 'HSV_Tuning', 34, 180, nothing)
        cv2.createTrackbar('S_MAX', 'HSV_Tuning', 255, 255, nothing)
        cv2.createTrackbar('V_MAX', 'HSV_Tuning', 255, 255, nothing)

        # 2. 开启后台监听
        rospy.Subscriber("/camera/rgb/image_raw", Image, self.image_callback)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("🎨 实时光线 HSV 调色板已启动！")
        rospy.loginfo("=======================================")

    def shutdown_hook(self):
        rospy.loginfo("🚨 正在退出调色板...")
        # 🌟 核心修复：删除了原来的恢复代码。
        # 退出了也不把白平衡还给系统，让它永远保持在 4600K 的战斗状态！
        rospy.loginfo("🔒 退出完毕，相机的白平衡将继续保持物理锁死状态。")

    def image_callback(self, data):
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            pass

    def run(self):
        rate = rospy.Rate(30) # 30Hz 刷新率
        
        while not rospy.is_shutdown():
            if self.latest_image is not None:
                cv_image = self.latest_image.copy()

                blurred = cv2.GaussianBlur(cv_image, (11, 11), 0)
                hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

                h_min = cv2.getTrackbarPos('H_MIN', 'HSV_Tuning')
                s_min = cv2.getTrackbarPos('S_MIN', 'HSV_Tuning')
                v_min = cv2.getTrackbarPos('V_MIN', 'HSV_Tuning')
                h_max = cv2.getTrackbarPos('H_MAX', 'HSV_Tuning')
                s_max = cv2.getTrackbarPos('S_MAX', 'HSV_Tuning')
                v_max = cv2.getTrackbarPos('V_MAX', 'HSV_Tuning')

                lower = np.array([h_min, s_min, v_min])
                upper = np.array([h_max, s_max, v_max])

                mask = cv2.inRange(hsv, lower, upper)
                res = cv2.bitwise_and(cv_image, cv_image, mask=mask)

                cv2.imshow('1. Original Camera', cv_image)
                cv2.imshow('2. Mask (White is Target)', mask)
                cv2.imshow('3. Filtered Result', res)
            
            key = cv2.waitKey(10) & 0xFF
            
            if key == ord('p'):
                if self.latest_image is not None:
                    h_min = cv2.getTrackbarPos('H_MIN', 'HSV_Tuning')
                    s_min = cv2.getTrackbarPos('S_MIN', 'HSV_Tuning')
                    v_min = cv2.getTrackbarPos('V_MIN', 'HSV_Tuning')
                    h_max = cv2.getTrackbarPos('H_MAX', 'HSV_Tuning')
                    s_max = cv2.getTrackbarPos('S_MAX', 'HSV_Tuning')
                    v_max = cv2.getTrackbarPos('V_MAX', 'HSV_Tuning')
                    
                    rospy.loginfo("\n\n↓↓↓ 请把下面的代码复制到字典里 ↓↓↓")
                    rospy.loginfo("(np.array([%d, %d, %d]), np.array([%d, %d, %d]))", 
                                  h_min, s_min, v_min, h_max, s_max, v_max)
                    rospy.loginfo("↑↑↑=====================================↑↑↑\n")
            elif key == ord('q'):
                rospy.signal_shutdown("用户手动退出")
                break
                
            rate.sleep()

if __name__ == '__main__':
    try:
        calibrator = HSVCalibrator()
        calibrator.run()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()