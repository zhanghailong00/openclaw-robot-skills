#!/usr/local/miniconda3/bin/python
"""
声音传感器脚本

功能：读取声音传感器的音量值，判断环境声音大小
硬件：智慧交通场景板上的声音检测传感器（Bscene 模块，模拟口 A1）
原理：analogRead(1) 返回 0-1023 的模拟值，值越大声音越大
阈值：400 约等于 1.95V，超过此值视为有声音

用法：
  python3 01_sound.py                    # 读取一次音量
  python3 01_sound.py --mode monitor     # 持续监测
  python3 01_sound.py --threshold 500    # 自定义阈值

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（声音传感器在 Bscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Bscene

# 声音传感器引脚（智慧交通场景板，模拟口 A1）
SOUND_PIN = 1

# 默认阈值（400 ≈ 1.95V，超过此值视为有声音）
DEFAULT_THRESHOLD = 400

# 命令行参数解析
parser = argparse.ArgumentParser(description="声音传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                    help="声音阈值 (0-1023)，默认 400")
parser.add_argument("--interval", type=float, default=0.2,
                    help="监测间隔（秒），默认 0.2")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 设置引脚为输入模式
    Bscene.pinMode(SOUND_PIN, "INPUT")

    if args.mode == "once":
        # 单次读取音量
        sensor_value = Bscene.analogRead(SOUND_PIN)
        has_sound = (sensor_value > args.threshold)
        result = {
            "success": True,
            "value": sensor_value,
            "has_sound": has_sound,
            "threshold": args.threshold
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测音量
        results = []
        for i in range(args.count):
            sensor_value = Bscene.analogRead(SOUND_PIN)
            has_sound = (sensor_value > args.threshold)
            results.append({
                "index": i + 1,
                "value": sensor_value,
                "has_sound": has_sound
            })
            if i < args.count - 1:
                time.sleep(args.interval)

        sound_count = sum(1 for r in results if r["has_sound"])
        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "sound_count": sound_count,
            "threshold": args.threshold,
            "results": results
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
