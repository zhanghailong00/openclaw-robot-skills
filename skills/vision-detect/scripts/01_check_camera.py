#!/usr/bin/env python3
"""测试摄像头 + 去畸变。"""
import sys
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft")
sys.path.insert(0, "/home/HwHiAiUser/arm_voice_soft/camera_utils")

from camera import Camera

cam = Camera()
cam.load_cam_calib_data()

print("=== 摄像头检测 ===")
print(f"  设备: video{cam.config['device']}")
print(f"  内参: fx={cam.f:.1f} cx={cam.cx:.1f} cy={cam.cy:.1f}")

cap = cam.get_video_capture()
import time
time.sleep(0.5)
cam.empty_cache()
ret, frame = cap.read()
cap.release()
cam.release()

if ret:
    undistorted = cam.remove_distortion(frame)
    print(f"  采集 OK: {frame.shape}")
    print(f"  去畸变 OK: {undistorted.shape}")
    print("结果：正常")
else:
    print("失败：无法采集")
    sys.exit(1)
