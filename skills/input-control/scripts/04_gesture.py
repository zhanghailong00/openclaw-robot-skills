#!/usr/local/miniconda3/bin/python
"""
手势传感器脚本

功能：识别 PAJ7620U2 手势传感器的 9 种手势
硬件：智慧家居场景板上的 PAJ7620U2 手势传感器（I2C 地址 0x73）
原理：通过 I2C 总线读取手势寄存器，识别上/下/左/右/前/后/顺时针/逆时针/挥动

支持的手势：
  Left / Right / Down / Up / Forward / Backward
  Clockwise / AntiClockwise / Wave

用法：
  python3 04_gesture.py                    # 读取一次手势
  python3 04_gesture.py --mode monitor     # 持续监测

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor/PAJ7620U2")
from gesture import PAJ7620U2

# 手势名称映射
GESTURE_NAMES = {
    0x001: "Left",
    0x002: "Right",
    0x004: "Down",
    0x008: "Up",
    0x010: "Forward",
    0x020: "Backward",
    0x040: "Clockwise",
    0x080: "AntiClockwise",
    0x100: "Wave"
}

# 命令行参数解析
parser = argparse.ArgumentParser(description="PAJ7620U2 手势传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.05,
                    help="监测间隔（秒），默认 0.05")
parser.add_argument("--count", type=int, default=100,
                    help="监测次数，默认 100")
args = parser.parse_args()

try:
    # 初始化手势传感器
    sensor = PAJ7620U2()

    if args.mode == "once":
        # 单次读取
        time.sleep(0.05)
        gesture_code = sensor.check_gesture()
        gesture_name = GESTURE_NAMES.get(gesture_code, "None")
        result = {
            "success": True,
            "gesture": gesture_name,
            "code": gesture_code
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        gesture_count = {}
        for i in range(args.count):
            time.sleep(args.interval)
            gesture_code = sensor.check_gesture()
            gesture_name = GESTURE_NAMES.get(gesture_code, "None")
            if gesture_name != "None":
                results.append({
                    "index": i + 1,
                    "gesture": gesture_name,
                    "code": gesture_code
                })
                gesture_count[gesture_name] = gesture_count.get(gesture_name, 0) + 1

        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "detected": len(results),
            "gesture_count": gesture_count,
            "results": results
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
