#!/usr/bin/env python3
"""
OLED 清屏脚本

功能：清空 OLED 显示屏上的所有内容
硬件：智能安防场景板上的 OLED 显示屏（SSD1306 驱动，I2C 通信）

用法：
  python3 02_oled_clear.py

输出：JSON 格式
"""
import sys, json

# 加载传感器驱动
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import oled_128_64 as oled

try:
    oled.init()           # 初始化 OLED
    oled.clearDisplay()   # 清屏
    print(json.dumps({"success": True}))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
