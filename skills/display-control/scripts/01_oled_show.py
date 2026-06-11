#!/usr/local/miniconda3/bin/python
"""
OLED 显示文字脚本

功能：在 128x64 OLED 小屏幕上显示 ASCII 文字
硬件：智能安防场景板上的 OLED 显示屏（SSD1306 驱动，I2C 通信）
限制：仅支持 ASCII 字符（32-127），不支持中文

用法：
  python3 01_oled_show.py --text "Hello"
  python3 01_oled_show.py --text "Hello World" --x 0 --y 3
  python3 01_oled_show.py --text "Temp:25C\nHumidity:60%"

输出：JSON 格式
"""
import sys, json, argparse

# 加载传感器驱动（OLED 模块在 python_sensor 目录下）
sys.path.insert(0, "/home/HwHiAiUser/.openclaw/workspace/python_sensor")
import oled_128_64 as oled

# 命令行参数解析
parser = argparse.ArgumentParser(description="OLED 文字显示")
parser.add_argument("--text", type=str, required=True, help="要显示的文字（仅 ASCII）")
parser.add_argument("--x", type=int, default=0, help="列位置（0-15），默认 0")
parser.add_argument("--y", type=int, default=0, help="行位置（0-7），默认 0")
args = parser.parse_args()

try:
    # 初始化 OLED（SSD1306 驱动）
    oled.init()
    oled.clearDisplay()       # 清屏
    oled.setNormalDisplay()   # 正常显示模式
    oled.setPageMode()        # 页地址模式（每页8行，共8页）

    # 支持多行显示（用 \n 分隔）
    lines = args.text.split("\\n")
    for i, line in enumerate(lines):
        y_pos = args.y + i
        if y_pos > 7:  # OLED 最多8行（0-7）
            break
        oled.setTextXY(args.x, y_pos)  # 设置光标位置
        oled.putString(line[:16])       # 每行最多16个字符

    result = {
        "success": True,
        "displayed": args.text,
        "lines": len(lines),
        "position": {"x": args.x, "y": args.y}
    }
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))
    sys.exit(1)
