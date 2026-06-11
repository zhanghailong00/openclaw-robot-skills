#!/usr/local/miniconda3/bin/python
"""
超声波距离传感器脚本

功能：读取超声波传感器测量的距离
硬件：智慧交通场景板上的超声波模块（Bscene 模块，D5 口）
原理：发送超声波脉冲，根据回波时间计算距离，返回值单位为 cm

用法：
  python3 02_ultrasonic.py                    # 读取一次距离
  python3 02_ultrasonic.py --mode monitor     # 持续监测
  python3 02_ultrasonic.py --mode monitor --count 5 --interval 1

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（超声波模块在 Bscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Bscene

# 超声波传感器引脚（智慧交通场景板，D5 口）
ULTRASONIC_PIN = 5

# 命令行参数解析
parser = argparse.ArgumentParser(description="超声波距离传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.5,
                    help="监测间隔（秒），默认 0.5")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    if args.mode == "once":
        # 单次读取距离（单位：cm）
        distance = Bscene.ultrasonicRead(ULTRASONIC_PIN)
        result = {
            "success": True,
            "distance_cm": distance,
            "unit": "cm"
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测距离（适用于传送带末端检测等场景）
        results = []
        for i in range(args.count):
            distance = Bscene.ultrasonicRead(ULTRASONIC_PIN)
            results.append({
                "index": i + 1,
                "distance_cm": distance
            })
            if i < args.count - 1:
                time.sleep(args.interval)

        min_dist = min(r["distance_cm"] for r in results)
        max_dist = max(r["distance_cm"] for r in results)
        avg_dist = sum(r["distance_cm"] for r in results) / len(results)

        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "min_cm": round(min_dist, 1),
            "max_cm": round(max_dist, 1),
            "avg_cm": round(avg_dist, 1),
            "results": results
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
