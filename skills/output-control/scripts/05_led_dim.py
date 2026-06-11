#!/usr/local/miniconda3/bin/python
"""
调光 LED 控制脚本

功能：控制智慧农业场景板上的调光 LED 亮度
硬件：智慧农业场景板上的调光 LED（Escene 模块，D3 口）
原理：通过 PWM 信号控制 LED 亮度（0-255，0=灭，255=最亮）
注意：D3、D5、D6 支持 PWM，D2、D4、D7、D8 不支持

用法：
  python3 05_led_dim.py --brightness 255     # 最亮
  python3 05_led_dim.py --brightness 128     # 半亮
  python3 05_led_dim.py --brightness 0       # 灭
  python3 05_led_dim.py --fade                # 渐变效果（0→255→0）

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（调光 LED 在 Escene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Escene

# LED 引脚（智慧农业场景板，D3 口，支持 PWM）
LED_PIN = 3

# 命令行参数解析
parser = argparse.ArgumentParser(description="调光 LED 控制")
parser.add_argument("--brightness", type=int, help="亮度值 (0-255)")
parser.add_argument("--fade", action="store_true", help="渐变效果（0→255→0）")
parser.add_argument("--off", action="store_true", help="关闭 LED")
args = parser.parse_args()

try:
    # 设置引脚为输出模式
    Escene.pinMode(LED_PIN, "OUTPUT")

    if args.off:
        # 关闭 LED
        Escene.analogWrite(LED_PIN, 0)
        result = {"success": True, "brightness": 0}

    elif args.brightness is not None:
        # 设置指定亮度（限制在 0-255 范围内）
        brightness = max(0, min(255, args.brightness))
        Escene.analogWrite(LED_PIN, brightness)
        result = {"success": True, "brightness": brightness}

    elif args.fade:
        # 渐变效果：0→255→0
        for i in range(0, 256, 10):
            Escene.analogWrite(LED_PIN, i)
            time.sleep(0.05)
        for i in range(255, -1, -10):
            Escene.analogWrite(LED_PIN, i)
            time.sleep(0.05)
        result = {"success": True, "action": "fade"}

    else:
        result = {"success": False, "error": "Specify --brightness, --fade, or --off"}

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
