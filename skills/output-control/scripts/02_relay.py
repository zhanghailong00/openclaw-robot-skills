#!/usr/local/miniconda3/bin/python
"""
继电器控制脚本

功能：控制智慧医疗场景板上的继电器开关
硬件：智慧医疗场景板上的继电器（Cscene 模块，D6 口）
原理：高电平(1)接通，低电平(0)断开

用法：
  python3 02_relay.py --action on     # 打开继电器
  python3 02_relay.py --action off    # 关闭继电器

输出：JSON 格式
"""
import sys, json, argparse

# 加载传感器驱动（继电器在 Cscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
from Cscene import *

# 继电器引脚（智慧医疗场景板，D6 口）
RELAY_PIN = 6

# 命令行参数解析
parser = argparse.ArgumentParser(description="继电器控制")
parser.add_argument("--action", choices=["on", "off"], required=True,
                    help="on=打开, off=关闭")
args = parser.parse_args()

try:
    # 设置引脚为输出模式
    pinMode(RELAY_PIN, "OUTPUT")

    if args.action == "on":
        # 打开继电器（高电平）
        digitalWrite(RELAY_PIN, 1)
        result = {"success": True, "action": "on"}

    elif args.action == "off":
        # 关闭继电器（低电平）
        digitalWrite(RELAY_PIN, 0)
        result = {"success": True, "action": "off"}

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
