#!/usr/bin/env python3
# coding: utf-8
# import sys
# # 强行把包含正确 models 的路径置顶！
# sys.path.insert(0, '/home/jetson/software/yolov5/')
import rospy
import cv2 as cv
import numpy as np
import time
import torch
from numpy import random
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

# ========== YOLOv5 依赖导入 ==========
from utils.torch_utils import select_device
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords, xyxy2xywh

# 确认你的模型路径是正确的
# model_path = '/home/jetson/software/yolov5/best.pt'
model_path = '/home/jetson/yahboomcar_ws/src/garbage_identify_yolov5/model0.pt'
# ========== 模型初始化 ==========
print("正在加载 YOLOv5 模型，请稍候...")
device = select_device()
model = attempt_load(model_path, map_location=device)

# 🌟 终极 PyTorch 兼容性魔法补丁：给所有 Upsample 层强行贴上缺失的属性！
for m in model.modules():
    if isinstance(m, torch.nn.Upsample):
        m.recompute_scale_factor = None

names = model.module.names if hasattr(model, 'module') else model.names
colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]
print("模型加载成功！包含类别:", names)

class garbage_identify:
    def __init__(self):
        self.img = None
        self.garbage_index = 0
        self.name = "None"

    def garbage_run(self, image):
        self.img = cv.resize(image, (640, 480))
        
        if self.garbage_index < 3:
            cv.putText(self.img, 'Model-Warming-Up...', (190, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            self.garbage_index += 1
            return self.img
            
        try: 
            self.get_pos()
        except Exception as e: 
            print("推理报错:", e)
            
        return self.img

    def get_pos(self):
        img = self.img.copy()
        img = np.transpose(img, (2, 0, 1))
        img = torch.from_numpy(img).to(device)
        img = img.float()
        img /= 255.0  

        if img.ndimension() == 3: 
            img = img.unsqueeze(0)

        pred = model(img)[0]
        pred = non_max_suppression(pred, 0.4, 0.5)

        if pred != [None] and len(pred[0]):
            for i, det in enumerate(pred): 
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], self.img.shape).round()
                
                for *xyxy, conf, cls in reversed(det):
                    label = '%s %.2f' % (names[int(cls)], conf)
                    color = colors[int(cls)]
                    
                    x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                    
                    # 画包围盒和标签
                    cv.rectangle(self.img, (x1, y1), (x2, y2), color, 2)
                    cv.putText(self.img, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                    
                    # 算一下中心点，画个红心
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    cv.circle(self.img, (cx, cy), 5, (0, 0, 255), -1)

# ========== ROS 纯净推流节点 ==========
class YOLOTopicPublisher:
    def __init__(self):
        rospy.init_node('yolo_topic_publisher', anonymous=True)
        self.bridge = CvBridge()
        self.yolo_detector = garbage_identify()
        
        # 1. 订阅底层摄像头
        self.sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.image_callback, queue_size=1)
        
        # 2. 🌟 新增：向外发布画好 YOLO 框的视频流话题！
        self.pub = rospy.Publisher("/yolo_result_image", Image, queue_size=1)
        
        print("📡 等待摄像头画面传入... 正在向 /yolo_result_image 话题推流！")

    def image_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            return

        # 送进 YOLO 大脑处理
        result_img = self.yolo_detector.garbage_run(cv_image)

        # 🌟 核心：把 OpenCV 图像重新打包成 ROS 图像并发出去！
        try:
            ros_img = self.bridge.cv2_to_imgmsg(result_img, "bgr8")
            self.pub.publish(ros_img)
        except CvBridgeError as e:
            pass

if __name__ == '__main__':
    try:
        publisher = YOLOTopicPublisher()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass