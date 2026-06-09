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
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/01_status.py
```

参数：无
用途：检查机械臂通信是否正常，获取当前关节角度和末端坐标

### 02_homing.py — 机械臂归零

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/02_homing.py
```

参数：无
用途：移动机械臂到安全位姿 (150, 0, 50)mm

### 03_gripper.py — 夹爪控制

```bash
# 打开夹爪
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action open

# 闭合夹爪
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py --action close

# 测试模式（开→闭完整流程，不加参数）
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/03_gripper.py
```

参数：`--action open` 或 `--action close`（不指定则执行测试）
输出示例：`{"success": true, "action": "open", "angle": 46.5}`

### 04_move_to.py — 移动到指定坐标

```bash
python3 /home/HwHiAiUser/.openclaw/workspace/skills/arm-basic/scripts/04_move_to.py --x 150 --y 50 --z 80
```

参数：
- `--x X`：X 坐标 (mm)，必填
- `--y Y`：Y 坐标 (mm)，必填
- `--z Z`：Z 坐标 (mm)，必填
- `--t T`：运动时间 (s)，可选，默认 0.75，越小越快

输出示例：`{"success": true, "target": {"x": 150.0, "y": 50.0, "z": 80.0}, "actual": {"x": 146.9, "y": -1.8, "z": 75.7}}`

## 使用规则

1. 首次操作前先调用 `01_status.py` 确认通信正常
2. 移动前确保工作台无遮挡
3. 脚本报错就停，不要盲目重试
4. 关节限位由脚本自动处理，不需要手动检查

## 典型调用流程

```
① 01_status.py          → 确认机械臂在线
② 02_homing.py          → 归零
③ 03_gripper.py --action open  → 打开夹爪
④ 04_move_to.py --x X --y Y --z Z  → 移动到目标
⑤ 03_gripper.py --action close → 夹取
⑥ 04_move_to.py --x X2 --y Y2 --z Z2  → 移动到放置位
⑦ 03_gripper.py --action open  → 松开
```
