#!/usr/bin/env python3
"""等待物体到达传送带末端（超声波检测）。"""
import sys, time

sys.path.insert(0, "/home/HwHiAiUser/orangepi_test")

try:
    import Bscene
except ImportError:
    print("失败：无法导入 Bscene 模块")
    sys.exit(1)

print("等待物体到达传送带末端（超声波检测）...")

while True:
    dist = Bscene.ultrasonicRead(5)
    print(f"  距离: {dist}cm")
    if dist <= 3:
        print("  检测到物体到达！✅")
        break
    time.sleep(0.2)

print("结果：物体已到达末端")
