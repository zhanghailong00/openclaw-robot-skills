---
name: input-control
description: 输入设备控制：摇杆、电位器、按键、手势识别。当用户提到摇杆、手柄、方向控制、电位器、旋钮、旋转角度、按键、按钮、开关、手势、挥手时使用。
allowed-tools: [exec]
---

# input-control

读取输入设备数据。每个脚本输出 JSON。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/`

## 脚本列表

### 01_joystick.py — 摇杆传感器

```bash
# 读取一次位置和方向
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/01_joystick.py

# 持续监测
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/01_joystick.py --mode monitor --count 10
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.5
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "x": 512, "y": 480, "direction": "center"}
```

方向判断：X/Y 值范围 0-1023，中心约 512
- X < 204 → left
- X > 819 → right
- Y < 204 → up
- Y > 819 → down
- 其他 → center

### 02_potentiometer.py — 电位器（旋转角度传感器）

```bash
# 读取一次角度
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/02_potentiometer.py

# 持续监测
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/02_potentiometer.py --mode monitor --count 10
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.5
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "value": 512, "voltage": 2.50, "degrees": 150.0}
```

### 03_button.py — 轻触按键

```bash
# 读取一次按键状态
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/03_button.py

# 持续监测（按键通常需要高频监测）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/03_button.py --mode monitor --count 100
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.1
- `--count N`：监测次数，默认 100

输出示例：
```json
{"success": true, "value": 0, "pressed": true}
```

### 04_gesture.py — 手势传感器

```bash
# 读取一次手势
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/04_gesture.py

# 持续监测（在传感器前挥手）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/04_gesture.py --mode monitor --count 100
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.05
- `--count N`：监测次数，默认 100

输出示例：
```json
{"success": true, "gesture": "Wave", "code": 256}
```

支持的手势：Left / Right / Down / Up / Forward / Backward / Clockwise / AntiClockwise / Wave

## 硬件说明

- 摇杆模块：安防模块 Ascene，模拟口 A0(X) / A1(Y)
- 电位器：医疗模块 Cscene，模拟口 A1
- 轻触按键：家居模块 Dscene，数字口 D5
- 手势传感器：家居模块 PAJ7620U2，I2C 地址 0x73
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor`
- 按键逻辑：digitalRead(5) == 0 表示按下，== 1 表示未按下
- 电位器满量程：0-300°，ADC 0-1023
