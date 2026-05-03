#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image, LaserScan, Range  
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge, CvBridgeError

from std_msgs.msg import Bool
from std_srvs.srv import SetBool, SetBoolResponse

from astra_common import simplePID

class ColorPIDAligner:
    def __init__(self):
        rospy.init_node('color_pid_align_node', anonymous=True)
        self.is_shutting_down = False
        rospy.on_shutdown(self.shutdown_hook)

        self.bridge = CvBridge()
        
        self.color_ranges = {
            'RED': [(np.array([0, 32, 36]), np.array([26, 255, 106]))],
            'BLUE': [(np.array([100, 145,9]), np.array([129, 255, 255]))],
            'GREEN': [(np.array([66,130,0]), np.array([90, 180, 84]))],
            'YELLOW': [(np.array([27, 161, 78]), np.array([48, 255, 255]))]
        }
        
        self.color_to_id = {'RED': 1, 'BLUE': 2, 'GREEN': 3, 'YELLOW': 4}
        
        self.target_pixel_x = 320  
        
        # ==========================================
        # 🌟 1. 物理距离目标设定
        # ==========================================
        self.target_dist_cm = 12.0     # 最终抓取时的贴脸距离 (12厘米)
        self.stage1_dist_cm = 16.0     # 第一阶段停下来扭雷达的安全距离 (16厘米)
        self.current_tof_dist_cm = None 
        
        # ==========================================
        # 🌟 2. 独立误差准许参数 (Deadband/Tolerance) -> 调参专区
        # ==========================================
        self.tol_dist_stage1 = 2.0     # 状态1：第一段距离误差允许范围 (cm) -> 默认 2.0
        self.tol_dist_final = 1.0      # 状态4：最终贴脸距离误差允许范围 (cm) -> 默认 1.0
        self.tol_yaw = 3             # 状态2/3：雷达转正偏航角误差允许 (度) -> 默认 2.5
        self.tol_pixel_rough = 30      # 状态1：像素粗调误差允许 (像素) -> 默认 30
        self.tol_pixel_fine = 2        # 状态5：最终极像素精调误差允许 (像素) -> 默认 3 (不建议设为1，极易震荡)

        # ==========================================
        # 🌟 3. 传感器滤波参数
        # ==========================================
        self.tof_alpha = 0.3           # ToF 距离一阶低通滤波系数 (0~1)。越小越平滑但延迟大，越大越灵敏但噪点多
        
        # PID 控制器 
        self.pid_x = simplePID(kp=0.007, ki=0.0, kd=0.001) 
        self.pid_y = simplePID(kp=0.004, ki=0.0, kd=0.0005) 
        self.pid_yaw = simplePID(kp=0.02, ki=0.0, kd=0.002) 

        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.debug_pub = rospy.Publisher('/camera/debug_vision', Image, queue_size=1)
        
        self.is_tracking_enabled = False
        self.align_done = False 
        
        self.locked_color = None 
        self.activation_time = rospy.Time.now()
        self.color_votes = {k: 0 for k in self.color_ranges.keys()}
        
        self.smooth_cx, self.smooth_cy = None, None
        self.smooth_lidar_angle = None 
        self.lidar_angle_error = 0.0
        self.is_lidar_valid = False

        self.work_state = 1  
        self.state_timer = None
        self.alignment_start_time = None

        self.toggle_srv = rospy.Service('/enable_redalign', SetBool, self.toggle_cb)
        self.success_pub = rospy.Publisher('/align_success', Bool, queue_size=1)

        rospy.Subscriber("/camera/rgb/image_raw", Image, self.color_callback, queue_size=1, buff_size=2**24)
        rospy.Subscriber("/scan", LaserScan, self.scan_callback, queue_size=1)
        rospy.Subscriber("/laser", Range, self.tof_callback, queue_size=1)
        
        rospy.loginfo("=======================================")
        rospy.loginfo("🚀 [误差参数化+距离滤波版] 智能分拣节点已启动！")
        rospy.loginfo("=======================================")

    # 🌟 【核心升级】ToF 滤波与安全装甲
    def tof_callback(self, msg):
        raw_dist_m = msg.range 
        
        # 1. 拦截无穷大 (inf) 和 非数字 (nan)
        if np.isinf(raw_dist_m) or np.isnan(raw_dist_m):
            return
            
        # 2. 扩大收信范围 (最大到8.0米)
        if raw_dist_m > 0.01 and raw_dist_m < 8.0: 
            new_dist_cm = raw_dist_m * 100.0
            
            # 3. 核心：一阶指数平滑滤波 (EMA Filter)
            if self.current_tof_dist_cm is None:
                self.current_tof_dist_cm = new_dist_cm # 第一次直接赋值
            else:
                self.current_tof_dist_cm = self.tof_alpha * new_dist_cm + (1 - self.tof_alpha) * self.current_tof_dist_cm

    def toggle_cb(self, req):
        self.is_tracking_enabled = req.data
        if self.is_tracking_enabled:
            rospy.loginfo("👁️ 收到唤醒指令！开始严格流程化任务...")
            self.pid_x.reset()
            self.pid_y.reset()
            self.pid_yaw.reset()
            self.align_done = False 
            
            self.locked_color = None 
            self.activation_time = rospy.Time.now()
            self.color_votes = {k: 0 for k in self.color_ranges.keys()}
            
            self.smooth_cx, self.smooth_cy = None, None
            self.smooth_lidar_angle = None 
            self.current_tof_dist_cm = None # 唤醒时重置距离滤波器
            self.is_lidar_valid = False
            self.work_state = 1
            self.state_timer = None
            self.alignment_start_time = None
        else:
            rospy.loginfo("💤 收到休眠指令！交出底盘！")
            self.cmd_pub.publish(Twist())
            
        return SetBoolResponse(success=True, message="Status Changed")

    def shutdown_hook(self):
        self.is_shutting_down = True
        for _ in range(5):
            self.cmd_pub.publish(Twist())
            rospy.sleep(0.05)

    def scan_callback(self, data):
        if not self.is_tracking_enabled or self.is_shutting_down or self.align_done:
            return

        ranges = np.array(data.ranges)
        ranges[np.isinf(ranges) | np.isnan(ranges)] = 0 
        
        angles = data.angle_min + np.arange(len(ranges)) * data.angle_increment
        angles = (angles + np.pi) % (2 * np.pi) - np.pi 
        
        ROI_ANGLE = np.radians(13) 
        DIST_MIN = 0.05
        DIST_MAX = 0.3 
        
        mask = (np.abs(angles) <= ROI_ANGLE) & (ranges > DIST_MIN) & (ranges < DIST_MAX)
        valid_ranges = ranges[mask]
        valid_angles = angles[mask]

        if len(valid_ranges) < 8:
            self.is_lidar_valid = False
            return

        sort_idx = np.argsort(valid_angles)
        valid_angles = valid_angles[sort_idx]
        valid_ranges = valid_ranges[sort_idx]
        diffs = np.abs(np.diff(valid_ranges))
        jump_indices = np.where(diffs > 0.05)[0] 
        if len(jump_indices) > 0:
            first_jump = jump_indices[0]
            valid_ranges = valid_ranges[:first_jump + 1]
            valid_angles = valid_angles[:first_jump + 1]
            
        if len(valid_ranges) < 8:
            self.is_lidar_valid = False
            return

        X = valid_ranges * np.cos(valid_angles) 
        Y = valid_ranges * np.sin(valid_angles) 
        
        k, _ = np.polyfit(Y, X, 1)
        raw_angle = np.degrees(np.arctan(k))

        if abs(raw_angle) > 35.0:
            self.is_lidar_valid = False
            return

        LIDAR_ALPHA = 0.3  
        if getattr(self, 'smooth_lidar_angle', None) is None:
            self.smooth_lidar_angle = raw_angle
        else:
            self.smooth_lidar_angle = LIDAR_ALPHA * raw_angle + (1 - LIDAR_ALPHA) * self.smooth_lidar_angle

        self.lidar_angle_error = self.smooth_lidar_angle
        self.is_lidar_valid = True

    def color_callback(self, data):
        if not self.is_tracking_enabled or self.is_shutting_down: 
            return

        if getattr(self, 'align_done', False):
            self.success_pub.publish(True)
            self.cmd_pub.publish(Twist()) 
            rospy.loginfo_throttle(2.0, "📡 物理对齐完美完成！正在发送交接信号...")
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError:
            return

        img_height, img_width = cv_image.shape[:2]
        self.target_pixel_x = int(img_width / 2)

        blurred = cv2.GaussianBlur(cv_image, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
        all_detected_blocks = []
        colors_to_scan = self.color_ranges.keys() if self.locked_color is None else [self.locked_color]

        for color_name in colors_to_scan:
            mask = np.zeros((img_height, img_width), dtype=np.uint8)
            ranges = self.color_ranges[color_name]
            for (lower, upper) in ranges:
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))
                
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)  
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2) 
                
            contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for c in contours:
                if cv2.contourArea(c) > 400: 
                    x, y, box_w, box_h = cv2.boundingRect(c)
                    aspect_ratio = float(box_w) / max(box_h, 1)
                    if 0.5 < aspect_ratio < 1.8: 
                        M = cv2.moments(c)
                        if M["m00"] > 0:
                            raw_cx = int(M["m10"] / M["m00"])
                            raw_cy = int(M["m01"] / M["m00"])
                            all_detected_blocks.append({
                                'color': color_name, 'raw_cx': raw_cx, 'raw_cy': raw_cy,
                                'w': box_w, 'h': box_h, 'x': x, 'y': y
                            })

        tracked_img = cv_image.copy()

        # 阶段 1：2秒黄金侦测阶段
        if self.locked_color is None:
            elapsed_time = (rospy.Time.now() - self.activation_time).to_sec()
            if elapsed_time < 2.0:
                if len(all_detected_blocks) > 0:
                    all_detected_blocks.sort(key=lambda b: b['raw_cx'], reverse=True)
                    candidate = all_detected_blocks[0]
                    self.color_votes[candidate['color']] += 1 
                    cv2.rectangle(tracked_img, (candidate['x'], candidate['y']), (candidate['x'] + candidate['w'], candidate['y'] + candidate['h']), (0, 255, 255), 2)
                    cv2.putText(tracked_img, "?[{}]?".format(candidate['color']), (candidate['x'], candidate['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                cv2.putText(tracked_img, "Observing... {:.1f}s".format(max(0.0, 2.0 - elapsed_time)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
                self.cmd_pub.publish(Twist())
                self.publish_debug_image(tracked_img)
                return  
            else:
                total_votes = sum(self.color_votes.values())
                if total_votes > 0:
                    self.locked_color = max(self.color_votes, key=self.color_votes.get)
                    rospy.loginfo("🔒 锁定目标颜色 [%s]", self.locked_color)
                else:
                    self.activation_time = rospy.Time.now()
                self.cmd_pub.publish(Twist())
                self.publish_debug_image(tracked_img)
                return  

        # 阶段 2：极速追踪阶段
        if len(all_detected_blocks) > 0:
            all_detected_blocks.sort(key=lambda b: b['raw_cx'], reverse=True)
            target = all_detected_blocks[0]
            
            ALPHA = 0.4 
            if getattr(self, 'smooth_cx', None) is None:
                self.smooth_cx, self.smooth_cy = target['raw_cx'], target['raw_cy']
            else:
                self.smooth_cx = ALPHA * target['raw_cx'] + (1 - ALPHA) * self.smooth_cx
                
            final_cx = int(self.smooth_cx)
            
            cv2.rectangle(tracked_img, (target['x'], target['y']), (target['x'] + target['w'], target['y'] + target['h']), (0, 255, 0), 3)
            cv2.circle(tracked_img, (final_cx, int(self.smooth_cy)), 5, (0, 0, 255), -1)
            
            # 显示状态和物理距离
            lidar_txt = f"Yaw: {self.lidar_angle_error:.1f}deg" if self.is_lidar_valid else "Yaw: N/A"
            tof_txt = f"ToF: {self.current_tof_dist_cm:.1f}cm" if self.current_tof_dist_cm else "ToF: WAIT"
            cv2.putText(tracked_img, f"St:{self.work_state} | {lidar_txt} | {tof_txt}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            twist_cmd = self.compute_approach_velocity(final_cx, target['color'])
            
            if not getattr(self, 'align_done', False):
                self.cmd_pub.publish(twist_cmd)
        else:
            self.pid_x.reset()
            self.pid_y.reset()
            self.pid_yaw.reset()
            self.work_state = 1 
            self.state_timer = None
            self.alignment_start_time = None
            self.smooth_cx, self.smooth_cy = None, None 
            self.smooth_lidar_angle = None 
            if not self.is_shutting_down:
                self.cmd_pub.publish(Twist())
                cv2.putText(tracked_img, "Lost block!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        self.publish_debug_image(tracked_img)

    def publish_debug_image(self, img):
        try:
            self.debug_pub.publish(self.bridge.cv2_to_imgmsg(img, "bgr8"))
        except CvBridgeError:
            pass

    # ==========================================
    # 🧠 【独立参数版】五段式刚性状态机
    # ==========================================
    def compute_approach_velocity(self, current_x, current_color):
        twist = Twist()
        error_pixel_y = self.target_pixel_x - current_x    
        
        # 保护机制：如果还没收到 ToF 数据，原地等待
        if self.current_tof_dist_cm is None:
            rospy.logwarn_throttle(1.0, "⏳ 等待 ToF 距离传感器数据...")
            return twist

        # 🛑 绝对安全红线防撞：如果比目标距离还近了 5cm，强制急刹车！
        if self.current_tof_dist_cm < (self.target_dist_cm - 5.0):
            twist.linear.x = 0.0
            twist.linear.y = 0.0
            twist.angular.z = 0.0
            self.pid_x.reset() 
            self.pid_y.reset()
            self.pid_yaw.reset()
            self.work_state = 1 
            rospy.logwarn_throttle(0.5, "🛑 距离过近强制防撞停车！距离: %.1f cm", self.current_tof_dist_cm)
            return twist

        # ----------------------------------------
        # 状态 1：第一段前进 (停在距纸箱 stage1_dist_cm 处准备扭雷达)
        # ----------------------------------------
        if self.work_state == 1:
            err_dist_1 = self.current_tof_dist_cm - self.stage1_dist_cm

            if abs(error_pixel_y) > self.tol_pixel_rough:
                vel_y = self.pid_y.compute(0, -error_pixel_y)
                twist.linear.y = max(min(vel_y, 0.15), -0.15)
                rospy.loginfo_throttle(0.5, "[状态 1] 粗调中心中...")
                
            elif err_dist_1 > self.tol_dist_stage1: 
                vel_y = self.pid_y.compute(0, -error_pixel_y)
                vel_x = self.pid_x.compute(0, -err_dist_1) 
                twist.linear.x = max(min(vel_x, 0.15), -0.15)
                twist.linear.y = max(min(vel_y, 0.15), -0.15)
                rospy.loginfo_throttle(0.5, "[状态 1] 第一段安全前进中... 距换挡点还有: %.1fcm", err_dist_1)
            else:
                twist.linear.x = 0.0
                twist.linear.y = 0.0
                rospy.loginfo("✅ [阶段切换] 达到 %.1fcm 换挡点，进入雷达转正！", self.stage1_dist_cm)
                self.work_state = 2

        # ----------------------------------------
        # 状态 2：雷达转正 
        # ----------------------------------------
        if self.work_state == 2:
            if not self.is_lidar_valid:
                rospy.logwarn_throttle(0.5, "等待雷达数据...")
                return twist

            if abs(self.lidar_angle_error) > self.tol_yaw:
                vel_z = self.pid_yaw.compute(0, self.lidar_angle_error)
                twist.angular.z = max(min(vel_z, 0.3), -0.3)
                rospy.loginfo_throttle(0.5, "[状态 2] 正在原地自转平行纸箱... 偏航角: %.1f°", self.lidar_angle_error)
            else:
                twist.angular.z = 0.0
                rospy.loginfo("✅ [阶段切换] 雷达已平齐，开始 1 秒稳态检测！")
                self.state_timer = rospy.Time.now()
                self.work_state = 3

        # ----------------------------------------
        # 状态 3：检测雷达平齐稳态 1 秒 
        # ----------------------------------------
        if self.work_state == 3:
            if abs(self.lidar_angle_error) > self.tol_yaw:
                rospy.logwarn("⚠️ 平齐状态被打破，退回状态 2 重新调整！")
                self.work_state = 2
                self.state_timer = None
                return twist

            elapsed = (rospy.Time.now() - self.state_timer).to_sec()
            if elapsed >= 1.0:
                rospy.loginfo("✅ [阶段切换] 1 秒稳态达成！进入最终贴脸前进！")
                # 👇 切入状态4前，先把稳态计时器清空交给状态4用
                self.state_timer = None
                self.work_state = 4
            else:
                rospy.loginfo_throttle(0.5, "[状态 3] 稳态倒计时... %.1f 秒", 1.0 - elapsed)

        # ----------------------------------------
        # 🌟 状态 4：第二段（最终）贴脸前进 + 1秒防冲过检测
        # ----------------------------------------
        if self.work_state == 4:
            err_dist_final = self.current_tof_dist_cm - self.target_dist_cm
            
            # 👇 注意这里改成了绝对值 abs()！意味着万一小车滑过头靠得太近，它会自动倒车修正！
            if abs(err_dist_final) > self.tol_dist_final: 
                # PID 控制器天然支持倒退，只要传负误差，它就会输出倒车速度
                vel_x = self.pid_x.compute(0, -err_dist_final)
                twist.linear.x = max(min(vel_x, 0.12), -0.12) 
                self.state_timer = None # 只要还在前后移动，就破坏稳态计时
                rospy.loginfo_throttle(0.5, "[状态 4] 贴脸微调中... 距离误差: %.1fcm", err_dist_final)
            else:
                twist.linear.x = 0.0
                # 👇 新增的 1秒贴脸稳态检测
                if self.state_timer is None:
                    self.state_timer = rospy.Time.now()
                    rospy.loginfo("🎯 刹车！进入贴脸 1 秒防冲过检测...")
                else:
                    elapsed = (rospy.Time.now() - self.state_timer).to_sec()
                    if elapsed >= 1.0:
                        rospy.loginfo("✅ [阶段切换] 物理距离稳如老狗！进入最后精调！")
                        self.work_state = 5
                    else:
                        rospy.loginfo_throttle(0.5, "⏳ 防过冲刹车检测中... 剩余 %.1f 秒", 1.0 - elapsed)

        # ----------------------------------------
        # 状态 5：左右极致精调与终极锁定 
        # ----------------------------------------
        if self.work_state == 5:
            if abs(error_pixel_y) > self.tol_pixel_fine:
                vel_y = self.pid_y.compute(0, -error_pixel_y)
                twist.linear.y = max(min(vel_y, 0.15), -0.15)
                self.alignment_start_time = None
                rospy.loginfo_throttle(0.5, "[状态 5] 消除最后的像素级偏差...")
            else:
                twist.linear.y = 0.0
                if self.alignment_start_time is None:
                    self.alignment_start_time = rospy.Time.now()
                    rospy.loginfo("🎯 距离与姿态绝对完美！开启抓取前 2 秒锁定倒计时...")
                else:
                    elapsed = (rospy.Time.now() - self.alignment_start_time).to_sec()
                    if elapsed >= 2.0:
                        target_id = self.color_to_id.get(current_color, 1) 
                        rospy.set_param('/current_aruco_id', target_id)
                        rospy.loginfo("🏆 [任务下发] 终极锁定完成！去寻找二维码 -> %d", target_id)
                        self.align_done = True
                    else:
                        rospy.loginfo_throttle(0.5, "⏳ 最终锁定中... 剩余 {:.1f} 秒".format(2.0 - elapsed))

        return twist

if __name__ == '__main__':
    try:
        ColorPIDAligner()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass