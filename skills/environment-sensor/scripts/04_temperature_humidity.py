#!/usr/local/miniconda3/bin/python
"""
温湿度传感器脚本

功能：读取 DHT11 温湿度传感器的温度和湿度
硬件：智慧农业场景板上的温湿度传感器（Escene 模块，D4 口，蓝色传感器）
原理：通过数字接口读取温度（°C）和湿度（%）

用法：
  python3 04_temperature_humidity.py                    # 读取一次
  python3 04_temperature_humidity.py --mode monitor     # 持续监测

输出：JSON 格式
"""
import sys, json, argparse, time
import math

# 加载传感器驱动（温湿度传感器在 Escene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Escene

# 温湿度传感器引脚（智慧农业场景板，D4 口）
SENSOR_PIN = 4

# 传感器类型：0=蓝色，1=白色
SENSOR_TYPE = 0  # 蓝色传感器

# 命令行参数解析
parser = argparse.ArgumentParser(description="温湿度传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=2.0,
                    help="监测间隔（秒），默认 2.0")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    def read_temp_humidity():
        """读取温度和湿度"""
        temp, humidity = Escene.dht(SENSOR_PIN, SENSOR_TYPE)
        return temp, humidity

    if args.mode == "once":
        # 单次读取
        temp, humidity = read_temp_humidity()
        if math.isnan(temp) or math.isnan(humidity):
            result = {
                "success": True,
                "valid": False,
                "message": "读取失败，请检查传感器"
            }
        else:
            result = {
                "success": True,
                "valid": True,
                "temperature_c": round(temp, 1),
                "humidity_percent": round(humidity, 1)
            }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        valid_count = 0
        for i in range(args.count):
            temp, humidity = read_temp_humidity()
            if not math.isnan(temp) and not math.isnan(humidity):
                results.append({
                    "index": i + 1,
                    "temperature_c": round(temp, 1),
                    "humidity_percent": round(humidity, 1)
                })
                valid_count += 1
            if i < args.count - 1:
                time.sleep(args.interval)

        if valid_count > 0:
            avg_temp = sum(r["temperature_c"] for r in results) / len(results)
            avg_humidity = sum(r["humidity_percent"] for r in results) / len(results)
            result = {
                "success": True,
                "valid": True,
                "avg_temperature_c": round(avg_temp, 1),
                "avg_humidity_percent": round(avg_humidity, 1),
                "total": args.count,
                "valid_count": valid_count,
                "results": results
            }
        else:
            result = {
                "success": True,
                "valid": False,
                "message": "所有读取均失败，请检查传感器"
            }
        print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
