#!/usr/bin/env python3
"""移动机械臂末端到指定坐标。

用法：
  python3 04_move_to.py --x 150 --y 50 --z 80
  python3 04_move_to.py --x 150 --y 50 --z 80 --t 0.5

参数：
  --x X    X 坐标 (mm)，必填
  --y Y    Y 坐标 (mm)，必填
  --z Z    Z 坐标 (mm)，必填
  --t T    运动时间 (s)，默认 0.75，越小越快

输出 JSON：
  {"success": true, "target": {"x": 150, "y": 50, "z": 80}, "actual": {"x": 150.1, "y": 49.8, "z": 80.2}}
"""
import sys, json, argparse
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

import logging
logging.basicConfig(level=logging.ERROR)

from arm4dof import Arm4DoF

parser = argparse.ArgumentParser(description="移动机械臂到指定坐标")
parser.add_argument("--x", type=float, required=True, help="X 坐标 (mm)")
parser.add_argument("--y", type=float, required=True, help="Y 坐标 (mm)")
parser.add_argument("--z", type=float, required=True, help="Z 坐标 (mm)")
parser.add_argument("--t", type=float, default=0.75, help="运动时间 (s)，默认 0.75")
args = parser.parse_args()

try:
    arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)
except Exception as e:
    print(json.dumps({"success": False, "error": f"机械臂连接失败: {str(e)}"}, ensure_ascii=False))
    sys.exit(1)

try:
    arm.move([args.x, args.y, args.z], t=args.t, wait=True)
    pose = arm.get_tool_pose()
    result = {
        "success": True,
        "target": {"x": round(args.x, 1), "y": round(args.y, 1), "z": round(args.z, 1)},
        "actual": {
            "x": round(float(pose[0]), 1),
            "y": round(float(pose[1]), 1),
            "z": round(float(pose[2]), 1)
        }
    }
    print(json.dumps(result, ensure_ascii=False))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
