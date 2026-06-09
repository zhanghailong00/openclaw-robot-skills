# OpenClaw Skill 分类与设计文档

## 设计原则

**按使用意图分类**，不按硬件模块分类。

AI 智能体（龙虾）根据用户的自然语言意图，自动选择对应的 Skill 调用。Skill 的名字和描述要让 AI 能"看懂"，而不是让人看懂。

```
学生说意图 → 龙虾选 Skill → 执行脚本 → 返回结果
```

## Skill 分类

### 第一类：硬件子系统（已有）

| Skill | 功能 | 包含脚本 |
|-------|------|---------|
| **arm-basic** | 机械臂控制 | 01_status, 02_homing, 03_gripper, 04_move_to |
| **vision-detect** | YOLO 目标检测 | 01_check_camera, 02_run_detection |
| **coord-transform** | 坐标转换 | 01_check_calib, 02_convert |
| **conveyor-belt** | 传送带控制 | 01_check_sensors, 02_belt_on, 03_belt_off, 04_wait_start, 05_wait_end |
| **arm-delivery** | 送餐流程（参考文档） | 无脚本，组合其他 Skill |

### 第二类：传感器与执行器（新增，按意图分）

| Skill | 意图 | 包含的硬件 | 状态 |
|-------|------|-----------|------|
| **environment-sensor** | "环境怎么样" | 温度、湿度、空气质量、光照 | ⏳ 待写 |
| **obstacle-sensor** | "前面有没有东西" | 红外光电开关、超声波测距 | ✅ 已完成 |
| **output-control** | "让它响/亮" | 蜂鸣器、继电器、LED 灯条 | ✅ 已完成 |
| **display-control** | "在屏幕上显示" | OLED 显示屏、数码管 | ⏳ 待写 |

## 意图 → Skill 映射表

| 用户说什么 | 调用哪个 Skill | 具体脚本 |
|-----------|---------------|---------|
| "读取机械臂状态" | arm-basic | 01_status.py |
| "把机械臂归零" | arm-basic | 02_homing.py |
| "打开夹爪" | arm-basic | 03_gripper.py --action open |
| "移动到 150, 50, 80" | arm-basic | 04_move_to.py --x 150 --y 50 --z 80 |
| "工作台上有什么" | vision-detect | 02_run_detection.py |
| "把像素坐标转成机械臂坐标" | coord-transform | 02_convert.py --px X --py Y --json |
| "打开传送带" | conveyor-belt | 02_belt_on.py |
| "传送带上有东西吗" | obstacle-sensor | 01_photoelectric.py |
| "温度多少" | environment-sensor | （待写） |
| "蜂鸣器响一下" | output-control | 01_buzzer.py --action beep |
| "屏幕上显示你好" | display-control | （待写） |
| "把汉堡放到盘子里" | arm-delivery | 龙虾自动编排多个 Skill |

## Skill 目录结构标准

每个 Skill 遵循以下结构：

```
skill-name/
├── SKILL.md                    ← AI 说明书（必须）
│   ├── YAML frontmatter        ← name + description（触发条件）
│   ├── 脚本列表                ← 完整命令 + 参数 + 输出示例
│   └── 硬件说明                ← 驱动路径、引脚、模块
└── scripts/                    ← 可执行脚本（必须）
    ├── 01_xxx.py
    └── 02_xxx.py
```

## SKILL.md 编写规范

### description 格式

```yaml
description: 做什么。当用户提到XX、YY、ZZ时使用。即使用户没有明确说"XX"，只要涉及AA、BB，也应该触发。
```

示例：
```yaml
description: 蜂鸣器控制。当用户提到蜂鸣器、响铃、报警、提示音时使用。即使用户没有明确说"蜂鸣器"，只要涉及"响一下"、"报警"，也应该触发。
```

### 脚本规范

- 输出必须是 JSON 格式
- 包含 `success` 字段
- 参数用 argparse 解析
- 错误时返回 `{"success": false, "error": "..."}`
- 驱动路径写完整路径

## 硬件驱动路径

| 驱动 | 路径 |
|------|------|
| 机械臂 SDK | `/home/HwHiAiUser/arm_voice_soft/` |
| 传感器驱动 | `/home/HwHiAiUser/.openclaw/workspace/python_sensor/` |
| Skill 目录 | `/home/HwHiAiUser/.openclaw/workspace/skills/` |

## 调用链路

```
飞书消息
  ↓
OpenClaw Gateway（DeepSeek AI）
  ↓ 读 SKILL.md，决定调用哪个 Skill
Python 脚本（scripts/*.py）
  ↓ import
传感器驱动（Ascene/Bscene/Cscene/Dscene/Escene.so）
  ↓ I2C 通信
硬件模块（传感器/执行器）
```
