---
name: conveyor-belt
description: 传送带控制：GPIO 启停 + 传感器检测。当用户提到传送带、传感器、运输物体时使用。即使用户没有明确说"传送带"，只要涉及"运输"、"传送"、"红外检测"、"超声波"，也应该触发。
allowed-tools: [exec]
---

# conveyor-belt

控制传送带启停，读取安防（红外）和交通（超声波）传感器。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/`

## 脚本列表

### 01_check_sensors.py — 检查传感器通信（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/01_check_sensors.py
```

参数：无
用途：检查安防模块、交通模块、GPIO 是否正常

### 02_belt_on.py — 启动传送带

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/02_belt_on.py
```

参数：无
用途：启动传送带电机

### 03_belt_off.py — 停止传送带

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/03_belt_off.py
```

参数：无
用途：停止传送带电机

### 04_wait_object_at_start.py — 等待物体到传送带起始端（阻塞）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/04_wait_object_at_start.py
```

参数：无
用途：阻塞等待，直到红外传感器检测到物体放到传送带起始端
返回：检测到物体后返回

### 05_wait_object_at_end.py — 等待物体到传送带末端（阻塞）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/conveyor-belt/scripts/05_wait_object_at_end.py
```

参数：无
用途：阻塞等待，直到超声波传感器检测到物体到达传送带末端（距离 <= 3cm）
返回：检测到物体后返回

## 传送带工作流程

```
① 机械臂把物体放到传送带起始端
② 04_wait_object_at_start.py → 等物体到位
③ 02_belt_on.py → 启动传送带
④ 05_wait_object_at_end.py → 等物体到达末端
⑤ 03_belt_off.py → 停止传送带
⑥ 机械臂从末端取走物体
```

## 注意事项

- 04 和 05 是阻塞脚本，会一直等到检测到物体才返回
- 建议：如果等待超过 60 秒未检测到物体，应中断流程检查硬件
- 超声波传感器检测距离 <= 3cm 视为物体到达
- 传送带启动后务必记得停止
