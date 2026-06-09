#!/usr/bin/env python3
"""
机械臂归零复位

功能：将机械臂移动到安全初始位姿 (150, 0, 50)mm
硬件：4-DOF 机械臂（UART 串口，/dev/ttyUSB1）
说明：归零后机械臂处于安全位置，可用于后续操作的起点

用法：
  python3 02_homing.py

输出：纯文本
"""
import sys

# 加载机械臂 SDK
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

import math, logging
logging.basicConfig(level=logging.WARN)

from arm4dof import Arm4DoF

try:
    arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
except Exception as e:
    print(f"失败：{e}")
    sys.exit(1)

print("归零中...")
arm.init_pose(t=0.75)

pose = arm.get_tool_pose()
print(f"末端位姿: ({pose[0]:.1f}, {pose[1]:.1f}, {pose[2]:.1f}, pitch={math.degrees(pose[3]):.1f}°)")

# 验证是否到达目标
if abs(pose[0] - 150) < 10 and abs(pose[2] - 50) < 10:
    print("结果：归零成功 ✅")
else:
    print(f"结果：警告 — 位姿偏差较大")
