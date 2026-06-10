#!/usr/bin/env python3
"""
轻触按键脚本

功能：读取轻触按键的状态（按下/未按下）
硬件：智慧家居场景板上的轻触按键（Dscene 模块，D5 口）
原理：digitalRead(5) 返回 0 表示按下，1 表示未按下

用法：
  python3 03_button.py                    # 读取一次
  python3 03_button.py --mode monitor     # 持续监测

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（按键在 Dscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Dscene

# 按键引脚（智慧家居场景板，D5 口）
BUTTON_PIN = 5

# 命令行参数解析
parser = argparse.ArgumentParser(description="轻触按键")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.1,
                    help="监测间隔（秒），默认 0.1")
parser.add_argument("--count", type=int, default=100,
                    help="监测次数，默认 100")
args = parser.parse_args()

try:
    # 设置引脚为输入模式
    Dscene.pinMode(BUTTON_PIN, "INPUT")

    if args.mode == "once":
        # 单次读取
        val = Dscene.digitalRead(BUTTON_PIN)
        pressed = (val == 0)
        result = {
            "success": True,
            "value": val,
            "pressed": pressed
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测（按键通常需要高频监测）
        results = []
        press_count = 0
        for i in range(args.count):
            val = Dscene.digitalRead(BUTTON_PIN)
            pressed = (val == 0)
            if pressed:
                press_count += 1
            results.append({
                "index": i + 1,
                "value": val,
                "pressed": pressed
            })
            if i < args.count - 1:
                time.sleep(args.interval)

        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "press_count": press_count,
            "results": results[-10:]  # 只返回最后 10 条
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
