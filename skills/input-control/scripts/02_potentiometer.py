#!/usr/local/miniconda3/bin/python
"""
电位器（旋转角度传感器）脚本

功能：读取电位器的旋转角度和电压值
硬件：智慧医疗场景板上的电位器（Cscene 模块，模拟口 A1）
原理：电位器输出 0-1023 的模拟值，对应 0-300° 旋转角度

用法：
  python3 02_potentiometer.py                    # 读取一次
  python3 02_potentiometer.py --mode monitor     # 持续监测
  python3 02_potentiometer.py --mode monitor --count 10

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（电位器在 Cscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Cscene

# 电位器引脚（智慧医疗场景板，模拟口 A1）
POT_PIN = 1

# ADC 参考电压 5V，电位器满量程 300°
ADC_REF = 5
VCC = 5
FULL_ANGLE = 300

# 命令行参数解析
parser = argparse.ArgumentParser(description="电位器（旋转角度传感器）")
parser.add_argument("--mode", choices=["once", "monitor"], default="once",
                    help="once=读取一次, monitor=持续监测")
parser.add_argument("--interval", type=float, default=0.5,
                    help="监测间隔（秒），默认 0.5")
parser.add_argument("--count", type=int, default=10,
                    help="监测次数，默认 10")
args = parser.parse_args()

try:
    # 设置引脚为输入模式
    Cscene.pinMode(POT_PIN, "INPUT")

    def read_pot():
        """读取电位器值，返回原始值、电压、角度"""
        sensor_value = Cscene.analogRead(POT_PIN)
        voltage = round(sensor_value * ADC_REF / 1023, 2)
        degrees = round(voltage * FULL_ANGLE / VCC, 1)
        return sensor_value, voltage, degrees

    if args.mode == "once":
        # 单次读取
        val, volt, deg = read_pot()
        result = {
            "success": True,
            "value": val,
            "voltage": volt,
            "degrees": deg
        }
        print(json.dumps(result, ensure_ascii=False))

    elif args.mode == "monitor":
        # 持续监测
        results = []
        for i in range(args.count):
            val, volt, deg = read_pot()
            results.append({
                "index": i + 1,
                "value": val,
                "voltage": volt,
                "degrees": deg
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
