---
name: input-control
description: 输入设备控制：摇杆位置读取。当用户提到摇杆、手柄、方向控制时使用。
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
python3 /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/01_joystick.py

# 持续监测
python3 /home/HwHiAiUser/.openclaw/workspace/skills/input-control/scripts/01_joystick.py --mode monitor --count 10
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

## 硬件说明

- 摇杆模块：安防模块 Ascene，模拟口 A0(X) / A1(Y)
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor`
- 驱动模块：Ascene（I2C 地址 0x0A）
