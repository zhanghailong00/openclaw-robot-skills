#!/usr/local/miniconda3/bin/python
"""
抓取并放置脚本（合并版，减少 Python 启动次数，提升速度）

功能：一次调用完成：开爪 → 转向 → 悬停 → 下降 → 夹取 → 抬起 → 移到放置位 → 下降 → 松开 → 抬起
硬件：4-DOF 机械臂（UART 串口，/dev/ttyUSB1）
优势：相比单独调用多个脚本，省掉 4-5 次 Python 启动时间
借鉴：robot_functions.py 的 grab_cubic() 流程，加上转向逻辑

用法：
  # 抓取并放到指定位置
  python3 05_grab_and_place.py --grab_x 154 --grab_y -50 --grab_z -31 --place_x 212 --place_y 62 --place_z 62

  # 只抓取不放置（放到安全位）
  python3 05_grab_and_place.py --grab_x 154 --grab_y -50 --grab_z -31

输出：JSON 格式
"""
import sys, json, argparse, time, math
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/utils_arm")

from arm4dof import Arm4DoF

# 命令行参数解析
parser = argparse.ArgumentParser(description="抓取并放置")
parser.add_argument("--grab_x", type=float, required=True, help="抓取位置 X (mm)")
parser.add_argument("--grab_y", type=float, required=True, help="抓取位置 Y (mm)")
parser.add_argument("--grab_z", type=float, required=True, help="抓取位置 Z (mm)")
parser.add_argument("--place_x", type=float, help="放置位置 X (mm)，不指定则放到安全位")
parser.add_argument("--place_y", type=float, help="放置位置 Y (mm)")
parser.add_argument("--place_z", type=float, help="放置位置 Z (mm)")
parser.add_argument("--t", type=float, default=0.75, help="运动时间 (s)，默认 0.75")
args = parser.parse_args()

try:
    arm = Arm4DoF(device="/dev/ttyUSB1", is_init_pose=False)

    # 1. 打开夹爪
    arm.gripper_open(degrees=25, t=0.5)

    # 2. 转向目标方向（借鉴 grab_cubic 的 atan2 逻辑）
    theta0 = math.atan2(args.grab_y, args.grab_x)
    arm.set_joint2({0: theta0}, T=0.5)

    # 3. 移动到抓取位置上方（悬停 25mm）
    arm.move([args.grab_x, args.grab_y, args.grab_z + 25], t=args.t, wait=True)

    # 4. 下降到抓取位置
    arm.move([args.grab_x, args.grab_y, args.grab_z], t=args.t, wait=True)
    time.sleep(0.3)

    # 5. 夹取
    arm.gripper_close(t=0.5)
    time.sleep(0.3)

    # 6. 抬起（50mm）
    arm.move([args.grab_x, args.grab_y, args.grab_z + 50], t=args.t, wait=True)

    if args.place_x is not None and args.place_y is not None and args.place_z is not None:
        # 7. 移动到放置位置上方
        arm.move([args.place_x, args.place_y, args.place_z + 25], t=args.t, wait=True)

        # 8. 下降到放置位置
        arm.move([args.place_x, args.place_y, args.place_z], t=args.t, wait=True)
        time.sleep(0.3)

        # 9. 松开
        arm.gripper_open(degrees=25, t=0.5)
        time.sleep(0.3)

        # 10. 抬起
        arm.move([args.place_x, args.place_y, args.place_z + 50], t=args.t, wait=True)

        result = {
            "success": True,
            "action": "grab_and_place",
            "grab": {"x": args.grab_x, "y": args.grab_y, "z": args.grab_z},
            "place": {"x": args.place_x, "y": args.place_y, "z": args.place_z}
        }
    else:
        # 没有指定放置位置，移到安全位
        arm.move([150, 0, 80], t=args.t, wait=True)
        result = {
            "success": True,
            "action": "grab_only",
            "grab": {"x": args.grab_x, "y": args.grab_y, "z": args.grab_z}
        }

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
