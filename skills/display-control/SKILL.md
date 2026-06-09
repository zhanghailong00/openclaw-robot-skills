---
name: display-control
description: 显示屏控制：OLED 显示文字、清屏、数码管显示数字。当用户提到屏幕显示、OLED、显示文字、显示数字时使用。即使用户没有明确说"显示"，只要涉及"屏幕上写"、"显示XX"，也应该触发。
allowed-tools: [exec]
---

# display-control

控制实训箱上的显示屏。每个脚本输出 JSON。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/display-control/scripts/`

## 脚本列表

### 01_oled_show.py — OLED 显示文字（仅支持 ASCII，不支持中文）

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/display-control/scripts/01_oled_show.py --text "Hello"
python3 /home/HwHiAiUser/.openclaw/workspace/skills/display-control/scripts/01_oled_show.py --text "Hello World" --x 0 --y 3
python3 /home/HwHiAiUser/.openclaw/workspace/skills/display-control/scripts/01_oled_show.py --text "Temp:25C\nHumidity:60%"
```

参数：
- `--text TEXT`：要显示的文字（必填，仅 ASCII）
- `--x N`：列位置（0-15），默认 0
- `--y N`：行位置（0-7），默认 0

输出示例：`{"success": true, "displayed": "Hello", "position": {"x": 0, "y": 0}}`

### 02_oled_clear.py — OLED 清屏

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/display-control/scripts/02_oled_clear.py
```

参数：无
输出示例：`{"success": true}`

### 03_digit_display.py — 4 位数码管显示

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/display-control/scripts/03_digit_display.py --value 1234
python3 /home/HwHiAiUser/.openclaw/workspace/skills/display-control/scripts/03_digit_display.py --value 12 --colon
```

参数：
- `--value N`：要显示的数字（0-9999）
- `--colon`：显示冒号（用于时间格式）

输出示例：`{"success": true, "displayed": 1234}`

## 硬件说明

- OLED 显示屏：128×64 像素，I2C 通信，SSD1306 驱动
- 4 位数码管：交通模块 Bscene
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor`
- OLED 仅支持 ASCII 字符（32-127），不支持中文
