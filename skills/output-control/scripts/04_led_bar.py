#!/usr/local/miniconda3/bin/python
"""
多彩 LED 灯条控制脚本

功能：控制智慧医疗场景板上的 5 颗多彩 LED 灯
硬件：智慧医疗场景板上的 LED 灯条（Cscene 模块，D3 口）
原理：每颗 LED 支持 4 种颜色（Green/Red/Yellow/Blue），通过 16 位颜色值控制

颜色编码：
  Green=1, Red=2, Yellow=3, Blue=4
  每颗 LED 占 3 位，5 颗 LED 共 15 位

用法：
  python3 04_led_bar.py --color green              # 全部亮绿色
  python3 04_led_bar.py --color red                # 全部亮红色
  python3 04_led_bar.py --pattern gradient         # 渐变效果（绿→黄→红）
  python3 04_led_bar.py --off                      # 全部关闭

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（LED 灯条在 Cscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Cscene

# LED 灯条引脚（智慧医疗场景板，D3 口）
LED_PIN = 3

# 颜色常量
COLORS = {
    "green": Cscene.Green,    # 1
    "red": Cscene.Red,        # 2
    "yellow": Cscene.Yellow,  # 3
    "blue": Cscene.Blue       # 4
}

# 命令行参数解析
parser = argparse.ArgumentParser(description="多彩 LED 灯条控制")
parser.add_argument("--color", choices=["green", "red", "yellow", "blue"],
                    help="全部 LED 显示指定颜色")
parser.add_argument("--pattern", choices=["gradient", "flash"],
                    help="渐变或闪烁效果")
parser.add_argument("--off", action="store_true", help="全部关闭")
args = parser.parse_args()

try:
    # 初始化 LED 灯条（5 颗 LED）
    Cscene.pinMode(LED_PIN, "OUTPUT")
    time.sleep(0.2)
    Cscene.LedBar_Init(LED_PIN, 0, 5)
    time.sleep(0.5)

    if args.off:
        # 关闭所有 LED
        Cscene.LedBar_Show(LED_PIN, 0, 0)
        result = {"success": True, "action": "off"}

    elif args.color:
        # 全部 LED 显示指定颜色
        color_val = COLORS[args.color]
        # 构建 16 位颜色值：5 颗 LED 各占 3 位
        color16bit = 0
        for i in range(5):
            color16bit = color16bit | (color_val << (i * 3))
        lowBits = color16bit & 255
        highBits = (color16bit & (255 << 8)) >> 8
        Cscene.LedBar_Show(LED_PIN, highBits, lowBits)
        result = {"success": True, "color": args.color}

    elif args.pattern == "gradient":
        # 渐变效果：绿 → 黄 → 红
        patterns = [
            # 全绿
            (Cscene.Green | (Cscene.Green << 3) | (Cscene.Green << 6) | (Cscene.Yellow << 9) | (Cscene.Red << 12)),
        ]
        # 简单闪烁：绿→红→绿
        for _ in range(3):
            # 绿
            color16bit = Cscene.Green | (Cscene.Green << 3) | (Cscene.Green << 6) | (Cscene.Yellow << 9) | (Cscene.Red << 12)
            lowBits = color16bit & 255
            highBits = (color16bit & (255 << 8)) >> 8
            Cscene.LedBar_Show(LED_PIN, highBits, lowBits)
            time.sleep(1)
            # 红
            color16bit = Cscene.Red | (Cscene.Red << 3) | (Cscene.Red << 6) | (Cscene.Red << 9) | (Cscene.Red << 12)
            lowBits = color16bit & 255
            highBits = (color16bit & (255 << 8)) >> 8
            Cscene.LedBar_Show(LED_PIN, highBits, lowBits)
            time.sleep(1)
        result = {"success": True, "pattern": "gradient"}

    elif args.pattern == "flash":
        # 闪烁效果
        for _ in range(5):
            color16bit = Cscene.Green | (Cscene.Green << 3) | (Cscene.Green << 6) | (Cscene.Green << 9) | (Cscene.Green << 12)
            lowBits = color16bit & 255
            highBits = (color16bit & (255 << 8)) >> 8
            Cscene.LedBar_Show(LED_PIN, highBits, lowBits)
            time.sleep(0.3)
            Cscene.LedBar_Show(LED_PIN, 0, 0)
            time.sleep(0.3)
        result = {"success": True, "pattern": "flash"}

    else:
        result = {"success": False, "error": "Specify --color, --pattern, or --off"}

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
