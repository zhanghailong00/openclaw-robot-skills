#!/usr/bin/env python3
"""
光敏电阻传感器脚本

功能：读取环境光照强度
硬件：智慧农业场景板上的光敏电阻（Dscene 模块，模拟口 A1）
原理：analogRead(1) 返回 0-1023 的模拟值，值越大光照越强
      电阻值 = (1023 - sensor_value) * 10 / sensor_value（单位 KΩ）

用法：
  python3 03_light.py                    # 读取一次
  python3 03_light.py --mode monitor     # 持续监测

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（光敏电阻在 Dscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Dscene

# 光敏电阻引脚（智慧农业场景板，模拟口 A1）
LIGHT_PIN = 1

# 命令行参数解析
parser = argparse.ArgumentParser(description="光敏电阻传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.5,
                    help="监测间隔（秒），默认 0.5")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 设置引脚为输入模式
    Dscene.pinMode(LIGHT_PIN, "INPUT")

    def read_light():
        """读取光照值，返回原始值、电阻值"""
        sensor_value = Dscene.analogRead(LIGHT_PIN)
        # 计算电阻值（KΩ），值越大光照越弱
        if sensor_value > 0:
            resistance = round((1023 - sensor_value) * 10 / sensor_value, 2)
        else:
            resistance = 9999.0
        return sensor_value, resistance

    if args.mode == "once":
        # 单次读取
        val, res = read_light()
        result = {
            "success": True,
            "value": val,
            "resistance_kohm": res
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        for i in range(args.count):
            val, res = read_light()
            results.append({
                "index": i + 1,
                "value": val,
                "resistance_kohm": res
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
