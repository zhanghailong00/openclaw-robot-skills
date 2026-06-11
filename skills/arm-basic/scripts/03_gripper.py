#!/usr/bin/env python3
"""
夹爪控制脚本

功能：控制机械臂末端夹爪的开合
硬件：4-DOF 机械臂上的夹爪舵机（ID=4，UART 串口通信）
原理：通过舵机角度控制夹爪开合，25°=打开，0°=闭合

用法：
  python3 03_gripper.py --action open      # 只打开
  python3 03_gripper.py --action close     # 只闭合
  python3 03_gripper.py                    # 测试模式（开→闭）

输出：JSON 格式（--action 模式）或纯文本（测试模式）
"""
import sys, json, argparse

# 加载机械臂 SDK
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

import logging
logging.basicConfig(level=logging.ERROR)

from arm4dof import Arm4DoF

parser = argparse.ArgumentParser()
parser.add_argument("--action", choices=["open", "close"], help="open 或 close，不指定则执行测试")
args = parser.parse_args()

try:
    arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)

try:
    if args.action == "open":
        arm.gripper_open(degrees=25, t=0.5)
        angle = arm.get_raw_angle_list()[4]
        print(json.dumps({"success": True, "action": "open", "angle": round(float(angle), 1)}, ensure_ascii=False))

    elif args.action == "close":
        arm.gripper_close(t=0.5)
        angle = arm.get_raw_angle_list()[4]
        print(json.dumps({"success": True, "action": "close", "angle": round(float(angle), 1)}, ensure_ascii=False))

    else:
        # 测试模式：开→闭
        print("=== 夹爪测试 ===")
        arm.gripper_open(degrees=25, t=0.5)
        a1 = arm.get_raw_angle_list()[4]
        print(f"  张开 (25°): 当前角度 {a1:.1f}°")

        arm.gripper_close(t=0.5)
        a2 = arm.get_raw_angle_list()[4]
        print(f"  闭合 (0°): 当前角度 {a2:.1f}°")

        print("结果：正常 ✅")

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
