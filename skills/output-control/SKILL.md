---
name: output-control
description: 输出设备控制：蜂鸣器、继电器、LED灯条。当用户提到蜂鸣器、响铃、报警、提示音、继电器、开关、灯光时使用。即使用户没有明确说"控制"，只要涉及"响一下"、"亮灯"、"开灯"、"关灯"，也应该触发。
allowed-tools: [exec]
---

# output-control

控制实训箱上的输出设备。每个脚本输出 JSON。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/`

## 脚本列表

### 01_buzzer.py — 蜂鸣器控制

```bash
# 蜂鸣器响（指定时长，单位秒）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/01_buzzer.py --action on --duration 2

# 蜂鸣器关闭
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/01_buzzer.py --action off

# 蜂鸣器响一下（默认 0.5 秒）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/01_buzzer.py --action beep
```

参数：
- `--action on`：持续响（需要手动 off 停止）
- `--action off`：关闭
- `--action beep`：响一下自动停
- `--duration N`：响铃时长（秒），默认 0.5，仅 beep 模式有效

输出示例：`{"success": true, "action": "beep", "duration": 0.5}`

### 02_relay.py — 继电器控制

```bash
# 打开继电器
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/02_relay.py --action on

# 关闭继电器
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/02_relay.py --action off
```

参数：
- `--action on`：打开继电器
- `--action off`：关闭继电器

输出示例：`{"success": true, "action": "on"}`

### 04_led_bar.py — 多彩 LED 灯条控制

```bash
# 全部亮绿色
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/04_led_bar.py --color green

# 全部亮红色
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/04_led_bar.py --color red

# 渐变闪烁效果
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/04_led_bar.py --pattern gradient

# 全部关闭
python3 /home/HwHiAiUser/.openclaw/workspace/skills/output-control/scripts/04_led_bar.py --off
```

参数：
- `--color`：green / red / yellow / blue
- `--pattern`：gradient（渐变）/ flash（闪烁）
- `--off`：全部关闭

输出示例：`{"success": true, "color": "green"}`

## 硬件说明

- 蜂鸣器：安防模块 Ascene，数字口 D3
- 多彩 LED 灯条：医疗模块 Cscene，数字口 D3（5 颗 LED）
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor`
- 驱动模块：Ascene（I2C 0x0A）、Cscene（I2C 0x0C）
