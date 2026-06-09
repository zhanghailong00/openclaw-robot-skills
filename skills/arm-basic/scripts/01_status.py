#!/usr/bin/env python3
"""
读取机械臂状态（只读，安全）

功能：查询 4-DOF 机械臂当前的关节角度和末端坐标
硬件：4-DOF 机械臂（UART 串口，/dev/ttyUSB1）
说明：此脚本不控制机械臂，只读取状态，用于确认通信正常

用法：
  python3 01_status.py

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
    print(f"失败：机械臂无法初始化 - {e}")
    print("  检查：串口线是否连接 /dev/ttyUSB1？")
    sys.exit(1)

raw = arm.get_raw_angle_list()
thetas = arm.get_thetas()
pose = arm.get_tool_pose()

print("=== 机械臂状态 ===")
names = ["J1(基座)", "J2(肩部)", "J3(肘部)", "J4(腕部)", "夹爪"]
for i, (r, t) in enumerate(zip(raw, thetas)):
    deg = math.degrees(t)
    print(f"  {names[i]}: 舵机={r:.1f}°  关节={deg:.1f}°")
print(f"末端位姿 (xyz+pitch): {pose}")
print(f"  -> Cartesian: ({pose[0]:.1f}, {pose[1]:.1f}, {pose[2]:.1f})mm")
print("结果：正常")
