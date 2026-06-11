---
name: environment-sensor
description: 环境感知：温度、湿度、声音、光照、加速度、空气质量、颜色。当用户提到温度、湿度、声音、音量、光照、亮度、空气、颜色、RGB时使用。即使用户没有明确说"检测"，只要涉及"温度多少"、"多亮"、"空气好吗"、"是什么颜色"，也应该触发。
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
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/01_sound.py

# 持续监测 10 次
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/01_sound.py --mode monitor --count 10

# 自定义阈值
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/01_sound.py --threshold 500
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
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/02_accelerometer.py

# 持续监测 5 次
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/02_accelerometer.py --mode monitor --count 5
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

### 03_light.py — 光敏电阻传感器

```bash
# 读取一次光照值
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/03_light.py

# 持续监测
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/03_light.py --mode monitor --count 10
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.5
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "value": 512, "resistance_kohm": 9.82}
```

### 04_temperature_humidity.py — 温湿度传感器

```bash
# 读取一次温湿度
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/04_temperature_humidity.py

# 持续监测
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/04_temperature_humidity.py --mode monitor --count 10
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 2.0
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "valid": true, "temperature_c": 25.3, "humidity_percent": 60.2}
```

### 05_air_quality.py — 空气质量传感器

```bash
# 读取一次空气质量
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/05_air_quality.py

# 持续监测
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/05_air_quality.py --mode monitor --count 10
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 0.5
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "value": 250, "level": "fresh"}
```

### 06_color.py — 颜色识别传感器

```bash
# 读取一次颜色
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/06_color.py

# 持续监测
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/environment-sensor/scripts/06_color.py --mode monitor --count 5
```

参数：
- `--mode once`：读取一次（默认）
- `--mode monitor`：持续监测
- `--interval N`：监测间隔（秒），默认 1.0
- `--count N`：监测次数，默认 10

输出示例：
```json
{"success": true, "r": 180, "g": 50, "b": 30, "lux": 320.5, "color_temp_k": 4500}
```

## 硬件说明

- 声音传感器：交通模块 Bscene，模拟口 A1
- 三轴加速度传感器：交通模块 MMA7660FC，I2C 地址 0x4C
- 光敏电阻：农业模块 Dscene，模拟口 A1
- 温湿度传感器：农业模块 Escene，D4 口（蓝色 DHT11）
- 空气质量传感器：农业模块 Escene，模拟口 A1
- 颜色传感器：农业模块 TCS34725，I2C 地址 0x29
- 污染等级：>700 高污染，>300 低污染，<=300 空气清新
- 注意：传感器需要预热 2 分钟才能稳定读数
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor`
