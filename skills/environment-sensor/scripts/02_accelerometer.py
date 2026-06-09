#!/usr/bin/env python3
"""
三轴加速度传感器脚本

功能：读取 MMA7660FC 三轴加速度传感器的 X/Y/Z 轴加速度值
硬件：智慧交通场景板上的 MMA7660FC 加速度传感器（I2C 地址 0x4C）
原理：通过 I2C 总线读取 6 位数字值（-32 ~ 31），可用于检测设备倾斜、运动

用法：
  python3 02_accelerometer.py                    # 读取一次
  python3 02_accelerometer.py --mode monitor     # 持续监测
  python3 02_accelerometer.py --mode monitor --count 5

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动路径
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
from MMA7660FC import MMA7660FC

# 命令行参数解析
parser = argparse.ArgumentParser(description="三轴加速度传感器")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=1.0,
                    help="监测间隔（秒），默认 1.0")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 初始化传感器（设置模式和采样率）
    mma = MMA7660FC()

    if args.mode == "once":
        # 单次读取
        mma.mode_config()
        mma.sample_rate_config()
        time.sleep(0.1)
        accl = mma.read_accl()
        result = {
            "success": True,
            "x": accl['x'],
            "y": accl['y'],
            "z": accl['z']
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        for i in range(args.count):
            mma.mode_config()
            mma.sample_rate_config()
            time.sleep(0.1)
            accl = mma.read_accl()
            results.append({
                "index": i + 1,
                "x": accl['x'],
                "y": accl['y'],
                "z": accl['z']
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
