#!/usr/bin/env python3
"""
4 位数码管显示脚本

功能：在 4 位 7 段数码管上显示数字
硬件：智慧交通场景板上的 4 位数码管（Bscene 模块，I2C 通信）
限制：只能显示 0-9999 的数字，支持冒号格式（用于时间显示）

用法：
  python3 03_digit_display.py --value 1234        # 显示数字
  python3 03_digit_display.py --value 1234 --colon # 带冒号显示
  python3 03_digit_display.py --off                # 关闭显示

输出：JSON 格式
"""
import sys, json, argparse, time

# 加载传感器驱动（数码管在 Bscene 模块上）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import Bscene

# 数码管引脚（智慧交通场景板，D2 口）
DIGIT_PIN = 2

# 命令行参数解析
parser = argparse.ArgumentParser(description="4 位数码管显示")
parser.add_argument("--value", type=int, help="要显示的数字 (0-9999)")
parser.add_argument("--colon", action="store_true", help="显示冒号（用于时间格式，如 12:30）")
parser.add_argument("--off", action="store_true", help="关闭显示")
args = parser.parse_args()

try:
    # 初始化数码管（必须步骤）
    Bscene.pinMode(DIGIT_PIN, "OUTPUT")   # 设置引脚为输出模式
    time.sleep(0.5)
    Bscene.fourDigit_init(DIGIT_PIN)      # 初始化 4 位数码管
    time.sleep(0.5)
    Bscene.fourDigit_brightness(DIGIT_PIN, 0)  # 设置亮度（0-7）
    time.sleep(0.5)

    if args.off:
        # 关闭数码管显示
        Bscene.fourDigit_off(DIGIT_PIN)
        result = {"success": True}

    elif args.value is not None:
        if args.colon:
            # 带冒号显示（如 12:30 → left=12, right=30）
            left = args.value // 100
            right = args.value % 100
            Bscene.fourDigit_score(DIGIT_PIN, left, right)
        else:
            # 普通数字显示
            Bscene.fourDigit_number(DIGIT_PIN, args.value, False)
        result = {"success": True, "displayed": args.value, "colon": args.colon}

    else:
        result = {"success": False, "error": "请指定 --value 或 --off"}

    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
