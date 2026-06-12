---
name: arm-basic
description: 4-DOF 机械臂控制：状态查询、归零、移动、夹爪。当用户提到移动机械臂、夹取、归零、抓取、放置时使用。即使用户没有明确说"机械臂"，只要涉及移动、夹爪、坐标，也应该触发。
allowed-tools: [exec]
---

# arm-basic

控制实训箱上的 4-DOF 机械臂。03 和 04 输出 JSON，01 和 02 输出纯文本。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/`

## 脚本列表

### 01_status.py — 读取机械臂状态（只读，安全）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/01_status.py
```

参数：无
用途：检查机械臂通信是否正常，获取当前关节角度和末端坐标

### 02_homing.py — 机械臂归零

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/02_homing.py
```

参数：无
用途：移动机械臂到安全位姿 (150, 0, 50)mm

### 03_gripper.py — 夹爪控制

```bash
# 打开夹爪
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action open

# 闭合夹爪
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action close

# 测试模式（开→闭完整流程，不加参数）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py
```

参数：`--action open` 或 `--action close`（不指定则执行测试）
输出示例：`{"success": true, "action": "open", "angle": 46.5}`

### 04_move_to.py — 移动到指定坐标

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 150 --y 50 --z 80
```

参数：
- `--x X`：X 坐标 (mm)，必填
- `--y Y`：Y 坐标 (mm)，必填
- `--z Z`：Z 坐标 (mm)，必填
- `--t T`：运动时间 (s)，可选，默认 0.75，越小越快

输出示例：`{"success": true, "target": {"x": 150.0, "y": 50.0, "z": 80.0}, "actual": {"x": 146.9, "y": -1.8, "z": 75.7}}`

### 05_grab_and_place.py — 抓取并放置（合并版，速度快，安全位过渡）

```bash
# 抓取物体，放到指定位置（默认经过安全位）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/05_grab_and_place.py --grab_x 154 --grab_y -50 --grab_z -31 --place_x 212 --place_y 62 --place_z 62

# 只抓取不放置（放到安全位）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/05_grab_and_place.py --grab_x 154 --grab_y -50 --grab_z -31

# 不经过安全位（连续操作时用）
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/05_grab_and_place.py --grab_x 154 --grab_y -50 --grab_z -31 --place_x 212 --place_y 62 --place_z 62 --no-safe
```

参数：
- `--grab_x X`：抓取位置 X (mm)，必填
- `--grab_y Y`：抓取位置 Y (mm)，必填
- `--grab_z Z`：抓取位置 Z (mm)，必填
- `--place_x X`：放置位置 X (mm)，可选
- `--place_y Y`：放置位置 Y (mm)，可选
- `--place_z Z`：放置位置 Z (mm)，可选
- `--t T`：运动时间 (s)，可选，默认 0.75
- `--no-safe`：不经过安全位（可选，默认经过安全位）

流程：
```
开爪 → 转向 → 悬停 → 下降 → 夹取 → 抬起
  → 安全位 (150, 0, 80)     ← 默认经过
  → 放置位上方 → 下降 → 松开 → 抬起
  → 安全位 (150, 0, 80)     ← 默认经过
```

输出示例：`{"success": true, "action": "grab_and_place", "grab": {"x": 154, "y": -50, "z": -31}, "place": {"x": 212, "y": 62, "z": 62}, "safe_pos": [150, 0, 80]}`

注意：
- 05 比单独调用 03+04 快很多，因为它只启动一次 Python 进程
- 默认经过安全位过渡，避免路径横甩
- 连续操作时可用 `--no-safe` 跳过安全位

## 使用规则

1. 首次操作前先调用 `01_status.py` 确认通信正常
2. 移动前确保工作台无遮挡
3. 脚本报错就停，不要盲目重试
4. 关节限位由脚本自动处理，不需要手动检查
5. 需要快速抓取放置时，优先使用 05_grab_and_place.py

## 典型调用流程

```
① 01_status.py          → 确认机械臂在线
② 02_homing.py          → 归零
③ 05_grab_and_place.py  → 抓取并放置（一步完成，自动经过安全位）
```

## 安全位说明

安全位坐标：`(150, 0, 80)mm`

- 抓取后会经过安全位再移动到放置位置
- 放置后会回到安全位再执行下一步操作
- 避免路径横甩，减少意外碰撞
- 可用 `--no-safe` 参数跳过（连续操作时）
