#!/usr/bin/env python3
"""
坐标转换脚本

功能：将像素坐标转换为机械臂可用的坐标
硬件：UVC 摄像头 + 4-DOF 机械臂
原理：像素 → 仿射变换 → 工作台坐标 → 齐次变换 → 机械臂坐标（含 Z 校正）

用法：
  python3 02_convert.py --px 320 --py 240
  python3 02_convert.py --px 320 --py 240 --json

输出：JSON 格式（加 --json）或纯文本
"""
import sys, os, argparse, json

PROJECT = "/home/HwHiAiUser/arm_voice_soft"
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "camera_utils"))

import numpy as np
import yaml
from camera import Camera
from image2workspace import Image2Workspace


def main():
    parser = argparse.ArgumentParser(description="像素坐标 -> 工作台坐标")
    parser.add_argument("--px", type=float, help="像素 X")
    parser.add_argument("--py", type=float, help="像素 Y")
    parser.add_argument("--cx", type=float, help="检测框中心 X")
    parser.add_argument("--cy", type=float, help="检测框中心 Y")
    parser.add_argument("--xmin", type=float)
    parser.add_argument("--ymin", type=float)
    parser.add_argument("--xmax", type=float)
    parser.add_argument("--ymax", type=float)
    parser.add_argument("--height", type=float, help="工件高度(mm)，默认用标定值")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON")
    args = parser.parse_args()

    # 确定像素坐标
    if args.px is not None and args.py is not None:
        px, py = args.px, args.py
    elif args.cx is not None and args.cy is not None:
        px, py = args.cx, args.cy
    elif args.xmin and args.ymin and args.xmax and args.ymax:
        px = (args.xmin + args.xmax) / 2
        py = (args.ymin + args.ymax) / 2
    else:
        print("提供像素坐标 (--px --py) 或检测框 (--cx --cy / --xmin --ymin --xmax --ymax)")
        sys.exit(1)

    # 初始化
    cam = Camera()
    cam.load_cam_calib_data()
    i2w = Image2Workspace(cam)

    # 工件高度
    with open(os.path.join(PROJECT, "config", "object.yaml"), "r") as f:
        obj = yaml.safe_load(f)
    h = args.height if args.height else obj["height"]

    # 如果指定高度，更新仿射矩阵
    if args.height is not None:
        i2w.update_affine_matrix(args.height)

    # 像素 -> 工作台
    wx, wy = i2w.img2workspace(px, py)

    # 工作台 -> 机械臂（含 Z 误差校正）
    z_coeff = np.loadtxt(os.path.join(PROJECT, "config", "z_error_polyfit.txt"), delimiter=",")
    z_poly = np.poly1d(z_coeff)
    T_aw = np.loadtxt(os.path.join(PROJECT, "config", "T_arm2ws.txt"), delimiter=",")
    wz = h * 0.5  # 物体中心
    wz_corrected = wz - float(z_poly(wz))
    aw = T_aw.dot(np.float32([wx, wy, wz_corrected, 1]))
    ax, ay, az = aw[0], aw[1], aw[2]

    result = {
        "pixel": {"x": round(px, 1), "y": round(py, 1)},
        "workspace": {"x": round(wx, 1), "y": round(wy, 1)},
        "z": round(wz, 1),
        "z_corrected": round(wz_corrected, 1),
        "arm_target": {"x": round(ax, 1), "y": round(ay, 1), "z": round(az, 1)}
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
        return

    print("=" * 60)
    print("坐标转换结果")
    print("=" * 60)
    print(f"  像素: ({px:.1f}, {py:.1f})")
    print(f"  工作台: ({wx:.1f}, {wy:.1f})mm")
    print(f"  工件高度: {h}mm, 抓取Z: {wz:.1f}mm")
    print(f"  校正后Z: {wz_corrected:.1f}mm (error={wz_corrected-wz:+.1f})")
    print(f"  机械臂目标: ({ax:.1f}, {ay:.1f}, {az:.1f})")
    print(f"  move([{ax:.1f}, {ay:.1f}, {az:.1f}])")
    print("结果：转换完成")


if __name__ == "__main__":
    main()
