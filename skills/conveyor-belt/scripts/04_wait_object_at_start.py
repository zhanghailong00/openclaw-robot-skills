#!/usr/local/miniconda3/bin/python
"""
等待安防模块红外传感器检测到物体（传送带起始端）。
阻塞直到检测到物体。
"""
import sys, time

sys.path.insert(0, "/home/HwHiAiUser/orangepi_test")

try:
    import Ascene
except ImportError:
    print("失败：无法导入 Ascene 模块")
    sys.exit(1)

print("等待物体到达传送带起始端（红外检测）...")

Ascene.pinMode(2, "INPUT")
time.sleep(0.1)

# 先读一次当前状态
last_val = Ascene.digitalRead(2)
print(f"  初始状态: {'有物体' if last_val == 0 else '无物体'}")

# 持续检测，直到有物体
while True:
    val = Ascene.digitalRead(2)
    if val == 0:  # 红外被遮挡 = 有物体
        print("  检测到物体！✅")
        break
    time.sleep(0.1)

print("结果：物体已到位")
