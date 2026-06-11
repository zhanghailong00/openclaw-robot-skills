---
name: obstacle-sensor
description: 障碍物检测：红外光电开关、超声波测距。当用户提到检测物体、有没有东西、距离多少、红外检测、超声波时使用。即使用户没有明确说"检测"，只要涉及"前面有没有"、"传送带上有没有东西"、"多远"，也应该触发。
allowed-tools: [exec]
---

# obstacle-sensor

检测障碍物和距离。每个脚本输出 JSON。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/obstacle-sensor/scripts/`

## 脚本列表

### 01_photoelectric.py — 红外光电开关检测

```bash
# 检测一次
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/obstacle-sensor/scripts/01_photoelectric.py

# 持续监测（每 0.5 秒检测一次，共 10 次）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/obstacle-sensor/scripts/01_photoelectric.py --mode monitor --interval 0.5 --count 10
```

参数：
- `--mode once`：检测一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.5
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "detected": true, "value": 0, "message": "检测到物体"}
```

### 02_ultrasonic.py — 超声波距离传感器

```bash
# 读取一次距离（单位：cm）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/obstacle-sensor/scripts/02_ultrasonic.py

# 持续监测 5 次，每次间隔 1 秒
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/obstacle-sensor/scripts/02_ultrasonic.py --mode monitor --count 5 --interval 1
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.5
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "distance_cm": 15.2, "unit": "cm"}
```

## 硬件说明

- 红外光电开关：安防模块 Ascene，数字口 D2
- 超声波传感器：交通模块 Bscene，数字口 D5
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor`
- 检测逻辑：digitalRead(2) == 0 表示检测到物体，== 1 表示无物体
- 超声波：ultrasonicRead(5) 返回距离（cm），传送带末端阈值 3cm
