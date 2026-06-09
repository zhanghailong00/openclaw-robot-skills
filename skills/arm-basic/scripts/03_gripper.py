#!/usr/bin/env python3
"""夹爪控制：支持 open/close 参数，也支持无参数测试模式。

用法：
  python3 03_gripper.py --action open      # 只打开
  python3 03_gripper.py --action close     # 只闭合
  python3 03_gripper.py                    # 测试模式（开→闭）
"""
import sys, json, argparse
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
        arm.gripper_open(degrees=45, t=0.5)
        angle = arm.get_raw_angle_list()[4]
        print(json.dumps({"success": True, "action": "open", "angle": round(float(angle), 1)}, ensure_ascii=False))

    elif args.action == "close":
        arm.gripper_close(t=0.5)
        angle = arm.get_raw_angle_list()[4]
        print(json.dumps({"success": True, "action": "close", "angle": round(float(angle), 1)}, ensure_ascii=False))

    else:
        # 测试模式：开→闭
        print("=== 夹爪测试 ===")
        arm.gripper_open(degrees=45, t=0.5)
        a1 = arm.get_raw_angle_list()[4]
        print(f"  张开 (45°): 当前角度 {a1:.1f}°")

        arm.gripper_close(t=0.5)
        a2 = arm.get_raw_angle_list()[4]
        print(f"  闭合 (0°): 当前角度 {a2:.1f}°")

        print("结果：正常 ✅")

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
