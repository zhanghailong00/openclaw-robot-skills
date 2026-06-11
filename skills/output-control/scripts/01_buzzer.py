#!/usr/local/miniconda3/bin/python
"""
蜂鸣器控制脚本

功能：控制有源蜂鸣器的响铃和关闭
硬件：智能安防场景板上的蜂鸣器（Ascene 模块，D3 口）
原理：高电平(127)响铃，低电平(0)关闭

用法：
  python3 01_buzzer.py --action beep               # 响一下（0.5秒）
  python3 01_buzzer.py --action beep --duration 2   # 响2秒
  python3 01_buzzer.py --action on                  # 持续响
  python3 01_buzzer.py --action off                 # 关闭

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（蜂鸣器在 Ascene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Ascene

# 蜂鸣器引脚（智能安防场景板，D3 口）
BUZZER_PIN = 3

# 命令行参数解析
parser = argparse.ArgumentParser(description="蜂鸣器控制")
parser.add_argument("--action", choices=["on", "off", "beep"], required=True,
                    help="on=持续响, off=关闭, beep=响一下")
parser.add_argument("--duration", type=float, default=0.5,
                    help="beep 模式的响铃时长（秒），默认 0.5")
args = parser.parse_args()

try:
    # 设置引脚为输出模式
    Ascene.pinMode(BUZZER_PIN, "OUTPUT")

    if args.action == "on":
        # 持续响（高电平 127 = 响）
        Ascene.analogWrite(BUZZER_PIN, 127)
        result = {"success": True, "action": "on"}

    elif args.action == "off":
        # 关闭（低电平 0 = 停）
        Ascene.analogWrite(BUZZER_PIN, 0)
        result = {"success": True, "action": "off"}

    elif args.action == "beep":
        # 响指定时长后自动关闭
        Ascene.analogWrite(BUZZER_PIN, 127)   # 开始响
        time.sleep(args.duration)               # 等待指定时长
        Ascene.analogWrite(BUZZER_PIN, 0)      # 关闭
        result = {"success": True, "action": "beep", "duration": args.duration}

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
