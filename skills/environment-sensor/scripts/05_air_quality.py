#!/usr/bin/env python3
"""
空气质量传感器脚本

功能：读取空气质量传感器的污染等级
硬件：智慧农业场景板上的空气质量传感器（Escene 模块，模拟口 A1）
原理：analogRead(1) 返回 0-1023 的模拟值，值越大空气越差
      > 700: 高污染
      > 300: 低污染
      <= 300: 空气清新
注意：传感器需要预热 2 分钟才能稳定读数

用法：
  python3 05_air_quality.py                    # 读取一次
  python3 05_air_quality.py --mode monitor     # 持续监测

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（空气质量传感器在 Escene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Escene

# 空气质量传感器引脚（智慧农业场景板，模拟口 A1）
AIR_PIN = 1

# 污染等级阈值
THRESHOLD_HIGH = 700
THRESHOLD_LOW = 300

# 命令行参数解析
parser = argparse.ArgumentParser(description="空气质量传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.5,
                    help="监测间隔（秒），默认 0.5")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 设置引脚为输入模式
    Escene.pinMode(AIR_PIN, "INPUT")

    def read_air_quality():
        """读取空气质量值，返回原始值和等级"""
        sensor_value = Escene.analogRead(AIR_PIN)
        if sensor_value > THRESHOLD_HIGH:
            level = "high_pollution"
        elif sensor_value > THRESHOLD_LOW:
            level = "low_pollution"
        else:
            level = "fresh"
        return sensor_value, level

    if args.mode == "once":
        # 单次读取
        val, level = read_air_quality()
        result = {
            "success": True,
            "value": val,
            "level": level
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        for i in range(args.count):
            val, level = read_air_quality()
            results.append({
                "index": i + 1,
                "value": val,
                "level": level
            })
            if i < args.count - 1:
                time.sleep(args.interval)

        avg_val = sum(r["value"] for r in results) / len(results)
        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "avg_value": round(avg_val, 1),
            "results": results
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
