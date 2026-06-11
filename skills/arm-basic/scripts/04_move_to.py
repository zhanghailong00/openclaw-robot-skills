#!/usr/local/miniconda3/bin/python
"""
移动机械臂末端到指定坐标

功能：控制 4-DOF 机械臂末端移动到指定的 (x, y, z) 坐标
硬件：4-DOF 机械臂（UART 串口舵机，/dev/ttyUSB1）
原理：逆运动学解算 → 最小抖动轨迹规划 → 舵机控制

用法：
  python3 04_move_to.py --x 150 --y 50 --z 80
  python3 04_move_to.py --x 150 --y 50 --z 80 --t 0.5

参数：
  --x X    X 坐标 (mm)，必填
  --y Y    Y 坐标 (mm)，必填
  --z Z    Z 坐标 (mm)，必填
  --t T    运动时间 (s)，默认 0.75，越小越快

输出：JSON 格式
"""
import sys, json, argparse

# 加载机械臂 SDK（arm4dof.py + 运动学模块）
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
