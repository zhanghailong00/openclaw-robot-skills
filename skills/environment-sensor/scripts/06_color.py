#!/usr/local/miniconda3/bin/python
"""
颜色识别传感器脚本

功能：读取 TCS34725 颜色传感器的 RGB 颜色值、光照度和色温
硬件：智慧农业场景板上的 TCS34725 颜色传感器（I2C 地址 0x29）
原理：通过红/绿/蓝/透明四通道光电二极管感知颜色，输出 RGB 值

用法：
  python3 06_color.py                    # 读取一次颜色
  python3 06_color.py --mode monitor     # 持续监测

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor/TCS34725")
from TCS34725 import TCS34725

# 命令行参数解析
parser = argparse.ArgumentParser(description="TCS34725 颜色传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=1.0,
                    help="监测间隔（秒），默认 1.0")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 初始化传感器
    sensor = TCS34725(0x29)
    if sensor.TCS34725_init() == 1:
        print(json.dumps({"success": False, "error": "TCS34725 初始化失败"}, ensure_ascii=False))
        sys.exit(1)
    time.sleep(2)  # 等待传感器稳定

    def read_color():
        """读取颜色值"""
        sensor.Get_RGBData()
        sensor.GetRGB888()
        lux = sensor.Get_Lux()
        color_temp = sensor.Get_ColorTemp()
        return {
            "r": int(sensor.RGB888_R),
            "g": int(sensor.RGB888_G),
            "b": int(sensor.RGB888_B),
            "lux": round(lux, 1),
            "color_temp_k": int(color_temp)
        }

    if args.mode == "once":
        # 单次读取
        color = read_color()
        result = {
            "success": True,
            "r": color["r"],
            "g": color["g"],
            "b": color["b"],
            "lux": color["lux"],
            "color_temp_k": color["color_temp_k"]
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        for i in range(args.count):
            color = read_color()
            results.append({
                "index": i + 1,
                "r": color["r"],
                "g": color["g"],
                "b": color["b"],
                "lux": color["lux"]
            })
            if i < args.count - 1:
                time.sleep(args.interval)

        avg_r = sum(r["r"] for r in results) / len(results)
        avg_g = sum(r["g"] for r in results) / len(results)
        avg_b = sum(r["b"] for r in results) / len(results)
        result = {
            "success": True,
            "mode": "monitor",
            "total": args.count,
            "avg_r": round(avg_r, 1),
            "avg_g": round(avg_g, 1),
            "avg_b": round(avg_b, 1),
            "results": results
        }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
