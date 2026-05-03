#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import cv2.aruco as aruco
import os
import glob

def test_aruco_in_folder():
    print("=======================================")
    print("🔍 启动加白边强化版 ArUco 探测器...")
    print("=======================================")

    # 涵盖工业界和机器人赛道 99% 的字典
    dict_to_test = {
        "DICT_4X4_50": aruco.DICT_4X4_50,
        "DICT_5X5_250": aruco.DICT_5X5_250,
        "DICT_6X6_250": aruco.DICT_6X6_250,
        "DICT_7X7_250": aruco.DICT_7X7_250,
        "APRILTAG_36h11": aruco.DICT_APRILTAG_36h11,
        "DICT_ARUCO_ORIGINAL": aruco.DICT_ARUCO_ORIGINAL
    }

    image_files = []
    for ext in ('*.png', '*.jpg', '*.jpeg'):
        image_files.extend(glob.glob(ext))
        
    image_files = [f for f in image_files if not f.startswith("result_")]

    if not image_files:
        print("⚠️ 当前文件夹下没有找到图片！")
        return

    for img_file in image_files:
        print(f"\n📂 正在读取图片: {img_file}")
        original_image = cv2.imread(img_file)
        
        if original_image is None:
            print("❌ 图片读取失败！")
            continue
            
        # 🔑 核心魔法：给图片四周强行加上 50 像素的纯白边框 (Quiet Zone)
        # 如果没有这圈白边，算法就找不到最外围的黑色正方形轮廓！
        image = cv2.copyMakeBorder(original_image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255])
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        found = False

        for dict_name, dict_type in dict_to_test.items():
            aruco_dict = aruco.Dictionary_get(dict_type)
            parameters = aruco.DetectorParameters_create()
            
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            
            if ids is not None and len(ids) > 0:
                print(f"✅ 破解成功！所属家族: [{dict_name}]")
                print(f"🎯 识别到 ID: {ids.flatten().tolist()}")
                
                aruco.drawDetectedMarkers(image, corners, ids)
                
                save_name = "result_" + img_file
                cv2.imwrite(save_name, image)
                print(f"💾 识别结果已保存为: {save_name}，快看看新加的白边和绿框！")
                
                found = True
                break 
                
        if not found:
            print("❌ 依然没有找到。这可能真的不是主流 ArUco 码。")

if __name__ == '__main__':
    test_aruco_in_folder()