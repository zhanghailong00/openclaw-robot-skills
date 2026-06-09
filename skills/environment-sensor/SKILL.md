---
name: environment-sensor
description: 环境感知：声音检测、温度、湿度。当用户提到声音、音量、多吵、温度、湿度时使用。即使用户没有明确说"检测"，只要涉及"环境怎么样"、"声音大吗"、"温度多少"，也应该触发。
allowed-tools: [exec]
---

# environment-sensor

检测环境参数。每个脚本输出 JSON。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/`

## 脚本列表

### 01_sound.py — 声音传感器

```bash
# 读取一次音量
python3 /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/01_sound.py

# 持续监测 10 次
python3 /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/01_sound.py --mode monitor --count 10

# 自定义阈值
python3 /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/01_sound.py --threshold 500
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--threshold N`：声音阈值 (0-1023)，默认 400
- `--interval N`：监测间隔（秒），默认 0.2
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "value": 520, "has_sound": true, "threshold": 400}
```

### 02_accelerometer.py — 三轴加速度传感器

```bash
# 读取一次加速度
python3 /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/02_accelerometer.py

# 持续监测 5 次
python3 /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/02_accelerometer.py --mode monitor --count 5
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 1.0
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "x": 0, "y": 0, "z": 32}
```

## 硬件说明

- 声音传感器：交通模块 Bscene，模拟口 A1
- 三轴加速度传感器：交通模块 MMA7660FC，I2C 地址 0x4C
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor`
- 读取值范围：-32 ~ 31（6 位数字值）
- 用途：检测设备倾斜、运动、姿态变化
