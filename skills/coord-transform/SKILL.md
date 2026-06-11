---
name: coord-transform
description: 坐标转换：像素坐标 → 机械臂坐标。当需要把视觉检测结果转换为机械臂可执行的坐标时使用。当用户提到"转换坐标"、"像素转机械臂"、或提供了像素坐标需要移动机械臂时触发。
allowed-tools: [exec]
---

# coord-transform

将摄像头像素坐标转换为机械臂可用的坐标。用于视觉引导抓取。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/coord-transform/scripts/`

## 脚本列表

### 01_check_calib.py — 验证标定数据（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/coord-transform/scripts/01_check_calib.py
```

参数：无
用途：检查标定文件是否完整，计算重投影误差（目标 < 5mm）

### 02_convert.py — 坐标转换（只读）

```bash
# 方式1：输入像素坐标
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/coord-transform/scripts/02_convert.py --px 320 --py 240 --json

# 方式2：输入检测框中心
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/coord-transform/scripts/02_convert.py --cx 240 --cy 185 --json

# 方式3：输入检测框坐标
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/coord-transform/scripts/02_convert.py --xmin 200 --ymin 150 --xmax 280 --ymax 220 --json
```

参数：
- `--px X --py Y`：像素坐标
- `--cx X --cy Y`：检测框中心坐标（和 --px --py 效果一样）
- `--xmin --ymin --xmax --ymax`：检测框坐标，自动计算中心
- `--height H`：工件高度 (mm)，可选，默认 25mm
- `--json`：输出 JSON 格式（推荐加上）

输出示例：
```json
{
  "pixel": {"x": 320.0, "y": 240.0},
  "workspace": {"x": 68.7, "y": -7.0},
  "z": 12.5,
  "z_corrected": 2.7,
  "arm_target": {"x": 216.8, "y": -2.4, "z": -31.2}
}
```

## 输出字段说明

| 字段 | 含义 |
|------|------|
| pixel.x, pixel.y | 输入的像素坐标 |
| workspace.x, workspace.y | 转换后的工作台坐标 (mm) |
| z | 理论抓取高度 (mm) |
| z_corrected | Z 轴误差校正后的高度 (mm) |
| arm_target.x/y/z | 机械臂目标坐标 (mm)，可直接传给 arm-basic 的 04_move_to.py |

## 典型调用流程

```
① vision-detect/02_run_detection.py → 拿到 cx=262, cy=165
② coord-transform/02_convert.py --px 262 --py 165 --json → 拿到 arm_target (154.6, -50.6, -31.2)
③ arm-basic/04_move_to.py --x 154.6 --y -50.6 --z -31.2
```
