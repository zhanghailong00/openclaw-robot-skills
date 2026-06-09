#!/usr/bin/env python3
"""归零复位：移动到初始位姿 (150, 0, 50)mm。"""
import sys
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
