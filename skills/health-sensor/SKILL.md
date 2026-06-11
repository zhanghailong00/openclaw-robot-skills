---
name: health-sensor
description: 健康检测：心率、血氧。当用户提到心率、脉搏、血氧、心跳、血压时使用。
allowed-tools: [exec]
---

# health-sensor

检测健康参数。每个脚本输出 JSON。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/health-sensor/scripts/`

## 脚本列表

### 01_pulse.py — 心率血氧传感器

```bash
# 读取心率和血氧（默认采集 5 秒）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/health-sensor/scripts/01_pulse.py

# 采集 10 秒数据（更准确）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/health-sensor/scripts/01_pulse.py --duration 10
```

参数：
- `--duration N`：数据采集时长（秒），默认 5

输出示例：
```json
{"success": true, "finger_detected": true, "heart_rate_bpm": 72.5, "spo2_percent": 98.2, "samples": 4}
```

## 硬件说明

- 心率血氧传感器：医疗模块 MAX30102，I2C 地址 0x57
- 驱动路径：`/home/HwHiAiUser/.openclaw/workspace/python_sensor/MAX30102`
- 使用方法：将手指放在传感器上，等待 5-10 秒采集数据
- 注意：需要 numpy 库支持计算
