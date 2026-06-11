#!/usr/local/miniconda3/bin/python
"""
红外光电开关检测脚本

功能：检测红外光电开关状态，判断前方是否有物体
硬件：智能安防场景板上的红外对管（Ascene 模块，D2 口）
原理：digitalRead(2) == 0 表示检测到物体，== 1 表示无物体

用法：
  python3 01_photoelectric.py                          # 检测一次
  python3 01_photoelectric.py --mode monitor            # 持续监测
  python3 01_photoelectric.py --mode monitor --interval 1 --count 5

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（红外光电开关在 Ascene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Ascene

# 红外光电开关引脚（智能安防场景板，D2 口）
PHOTO_PIN = 2

# 命令行参数解析
parser = argparse.ArgumentParser(description="红外光电开关检测")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=检测一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.5,
                    help="监测间隔（秒），默认 0.5")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 设置引脚为输入模式
    Ascene.pinMode(PHOTO_PIN, "INPUT")

    if args.mode == "once":
        # 单次检测
        val = Ascene.digitalRead(PHOTO_PIN)
        detected = (val == 0)  # 0=有物体, 1=无物体
        result = {
            "success": True,
            "detected": detected,
            "value": val
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测（适用于传送带等场景）
        results = []
        for i in range(args.count):
            val = Ascene.digitalRead(PHOTO_PIN)
            detected = (val == 0)
            results.append({
                "index": i + 1,
                "detected": detected,
                "value": val
            })
            if i < args.count - 1:
                time.sleep(args.interval)

        detected_count = sum(1 for r in results if r["detected"])
        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "detected_count": detected_count,
            "results": results
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
