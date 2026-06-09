#!/usr/bin/env python3
"""
检查所有坐标转换标定文件 + 重投影误差验证
"""
import sys, os, math

PROJECT = "/home/HwHiAiUser/arm_voice_soft"
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, "camera_utils"))

import numpy as np
import yaml

print("=" * 60)
print("坐标转换标定验证")
print("=" * 60)

CFG = os.path.join(PROJECT, "config")

# 1. 基本配置
print("\n[1] 基本配置")
with open(os.path.join(CFG, "handeye_9points.yaml"), "r") as f:
    he = yaml.safe_load(f)
    x0 = 0.5 * he["board_height"]
    y0 = 0.5 * he["board_width"]
    print(f"  标定板: {he['board_width']}x{he['board_height']}mm  (网格x0={x0}, y0={y0})")
    print(f"  延长杆: {he['pencil_length']}mm")

with open(os.path.join(CFG, "object.yaml"), "r") as f:
    obj = yaml.safe_load(f)
    print(f"  物体高度: {obj['height']}mm")

# 2. 变换矩阵
print("\n[2] 变换矩阵")
T_cam2ws = np.loadtxt(os.path.join(CFG, "T_cam2ws.txt"), delimiter=",")
T_arm2ws = np.loadtxt(os.path.join(CFG, "T_arm2ws.txt"), delimiter=",")
print(f"  T_cam2ws 平移: ({T_cam2ws[0,3]:.1f}, {T_cam2ws[1,3]:.1f}, {T_cam2ws[2,3]:.1f})mm")
print(f"  T_arm2ws 平移: ({T_arm2ws[0,3]:.1f}, {T_arm2ws[1,3]:.1f}, {T_arm2ws[2,3]:.1f})mm")

# 3. 相机参数
print("\n[3] 相机参数")
M = np.loadtxt(os.path.join(CFG, "M_intrisic.txt"), delimiter=",")
D = np.loadtxt(os.path.join(CFG, "distor_coeff.txt"), delimiter=",")
print(f"  内参: fx={M[0,0]:.2f} fy={M[1,1]:.2f} cx={M[0,2]:.2f} cy={M[1,2]:.2f}")
print(f"  畸变: k1={D[0]:.3f} k2={D[1]:.3f} p1={D[2]:.3f} p2={D[3]:.3f} k3={D[4]:.3f}")

# 4. Z 误差校正
print("\n[4] Z 轴误差校正")
z_coeff = np.loadtxt(os.path.join(CFG, "z_error_polyfit.txt"), delimiter=",")
z_poly = np.poly1d(z_coeff)
print(f"  多项式: error = {z_coeff[0]:.4f}*z + {z_coeff[1]:.4f}")
for z in [0, 10, 20, 30]:
    print(f"    z={z:>2d}mm -> 校正={z - float(z_poly(z)):.2f}mm")

# 5. 九点数据
print("\n[5] 九点标定数据")
img9 = np.loadtxt(os.path.join(CFG, "img9points.txt"), delimiter=",")
arm9 = np.loadtxt(os.path.join(CFG, "arm9points.txt"), delimiter=",")
print(f"  图像九点: {img9.shape}")
print(f"  机械臂九点: {arm9.shape}")
for i in range(9):
    print(f"    P{i}: img({img9[i,0]:3.0f},{img9[i,1]:3.0f}) arm({arm9[i,0]:.1f},{arm9[i,1]:.1f},{arm9[i,2]:.1f})")

# 6. 重投影误差验证
print("\n[6] 重投影误差验证")
try:
    from camera import Camera
    from image2workspace import Image2Workspace
    
    cam = Camera()
    cam.load_cam_calib_data()
    i2w = Image2Workspace(cam)
    
    x0 = 0.5 * he["board_height"]
    y0 = 0.5 * he["board_width"]
    ws_gts = np.float64([
        [x0,y0],[x0,0],[x0,-y0],
        [0,y0],[0,0],[0,-y0],
        [-x0,y0],[-x0,0],[-x0,-y0]
    ])
    
    errs = []
    for i in range(9):
        wx, wy = i2w.img2workspace(*img9[i])
        err = math.sqrt((wx-ws_gts[i,0])**2 + (wy-ws_gts[i,1])**2)
        errs.append(err)
        print(f"    P{i}: ws({wx:7.2f},{wy:7.2f}) vs gt({ws_gts[i,0]:6.1f},{ws_gts[i,1]:6.1f}) err={err:.2f}mm")
    
    avg = sum(errs) / len(errs)
    print(f"\n  平均误差: {avg:.2f}mm", end="")
    if avg < 2:
        print("  ✅ 优秀")
    elif avg < 5:
        print("  ⚠️ 可接受")
    else:
        print("  ❌ 需重新标定")
except Exception as e:
    print(f"  验证失败: {e}")

print("\n结果：检查完成")
