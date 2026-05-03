#!/bin/bash

echo "=========================================="
echo "🛡️ 正在执行 Astra 相机底层物理封印..."
echo "=========================================="

echo "-> 1. 正在关闭自动白平衡 (AWB)..."
rosservice call /camera/set_auto_white_balance false
sleep 2

echo "-> 2. 正在锁死色温 (当前设定: 4600K)..."
rosservice call /camera/set_white_balance 4600
sleep 2

echo "-> 3. 正在关闭背光补偿..."
v4l2-ctl -d /dev/video0 --set-ctrl=backlight_compensation=0
sleep 2

echo "-> 4. 正在关闭自动曝光优先..."
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_auto_priority=0
sleep 2

echo "=========================================="
echo "✅ 封印完成！相机已进入绝对恒定模式！"
echo "=========================================="