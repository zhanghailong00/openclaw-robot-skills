#!/usr/bin/env python3
"""
摇杆传感器脚本

功能：读取摇杆的 X/Y 轴位置和方向
硬件：智能安防场景板上的摇杆模块（Ascene 模块，模拟口 A0/A1）
原理：X/Y 轴各输出 0-1023 的模拟值，中心位置约 512
      X < 204 = 左，X > 819 = 右
      Y < 204 = 上，Y > 819 = 下

用法：
  python3 01_joystick.py                    # 读取一次
  python3 01_joystick.py --mode monitor     # 持续监测

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（摇杆在 Ascene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Ascene

# 摇杆引脚（智能安防场景板，模拟口 A0/A1）
X_PIN = 0
Y_PIN = 1

# 方向阈值（1024/5 = 204）
THRESHOLD = 204

# 命令行参数解析
parser = argparse.ArgumentParser(description="摇杆传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.5,
                    help="监测间隔（秒），默认 0.5")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 设置引脚为输入模式
    Ascene.pinMode(X_PIN, "INPUT")
    Ascene.pinMode(Y_PIN, "INPUT")

    def get_direction(x, y):
        """根据 X/Y 值判断方向"""
        if x < THRESHOLD:
            return "left"
        elif x > (1024 - THRESHOLD):
            return "right"
        elif y < THRESHOLD:
            return "up"
        elif y > (1024 - THRESHOLD):
            return "down"
        else:
            return "center"

    if args.mode == "once":
        # 单次读取
        x = Ascene.analogRead(X_PIN)
        y = Ascene.analogRead(Y_PIN)
        direction = get_direction(x, y)
        result = {
            "success": True,
            "x": x,
            "y": y,
            "direction": direction
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        for i in range(args.count):
            x = Ascene.analogRead(X_PIN)
            y = Ascene.analogRead(Y_PIN)
            direction = get_direction(x, y)
            results.append({
                "index": i + 1,
                "x": x,
                "y": y,
                "direction": direction
            })
            if i < args.count - 1:
                time.sleep(args.interval)

        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "results": results
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
