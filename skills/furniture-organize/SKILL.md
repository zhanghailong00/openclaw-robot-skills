---
name: furniture-organize
description: 家具整理：视觉识别桌面物品，按优先级分类抓取，路径规划避障，放置到指定区域。当用户提到整理桌子、收拾东西、分类物品、整理家具时使用。
allowed-tools: [exec]
---

# furniture-organize

桌面物品整理技能：自动识别、优先级排序、路径规划、抓取放置。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/`

## 脚本列表

### 01_detect_and_sort.py — 检测 + 优先级排序（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/01_detect_and_sort.py
```

参数：无
用途：调用 YOLO 检测桌面物品，按优先级排序后输出物品列表

输出示例：
```json
{
  "objects": [
    {"class": "cola", "label": "可乐", "cx": 240.0, "cy": 185.0, "priority": 3, "rank": 1},
    {"class": "hanbao", "label": "汉堡", "cx": 320.0, "cy": 200.0, "priority": 2, "rank": 2},
    {"class": "shutiao", "label": "薯条", "cx": 180.0, "cy": 150.0, "priority": 1, "rank": 3}
  ],
  "count": 3,
  "status": "ok"
}
```

### 02_plan_path.py — 路径规划（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/02_plan_path.py --start 150,0,80 --end 215,70,-31
```

参数：
- `--start x,y,z`：起点坐标（机械臂坐标，默认150,0,80）
- `--end x,y,z`：终点坐标（机械臂坐标）
- `--obstacles x1,y1,z1,r1;x2,y2,z2,r2`：障碍物列表（可选）

输出示例：
```json
{
  "path": [
    {"action": "move", "position": [150, 0, 80], "comment": "当前位置"},
    {"action": "move", "position": [215, 70, 80], "comment": "移动到目标上方"},
    {"action": "move", "position": [215, 70, -31], "comment": "下降到目标位置"}
  ],
  "step_count": 3,
  "has_obstacle": false,
  "status": "ok"
}
```

### 03_grab_and_place.py — 抓取放置执行（写操作）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/03_grab_and_place.py --obj cola --place 100,50,-31
```

参数：
- `--obj class_name`：物品类别（cola/hanbao/shutiao）
- `--place x,y,z`：放置位置坐标（机械臂坐标）
- `--grab-pos x,y,z`：抓取位置坐标（可选，默认从视觉获取）

输出示例：
```json
{
  "object": "cola",
  "label": "可乐",
  "grab_position": {"x": 215.0, "y": 69.9, "z": -31.2},
  "place_position": {"x": 100.0, "y": 50.0, "z": -31.2},
  "path_steps": 7,
  "status": "ok"
}
```

### 04_run_organize.py — 主流程（写操作）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/04_run_organize.py
```

参数：
- `--dry-run`：只规划不执行（调试用）
- `--place-zone x,y,width,height`：放置区域（可选）

用途：完整的整理流程：检测 → 排序 → 规划 → 抓取 → 放置

输出示例：
```json
{
  "total_objects": 3,
  "success_count": 3,
  "fail_count": 0,
  "details": [
    {"object": "cola", "status": "ok"},
    {"object": "hanbao", "status": "ok"},
    {"object": "shutiao", "status": "ok"}
  ],
  "status": "ok"
}
```

## 优先级规则

| 优先级 | 物品 | 说明 |
|--------|------|------|
| 3（最高） | 可乐 | 饮料先放，防止倾倒 |
| 2 | 汉堡 | 主食其次 |
| 1（最低） | 薯条 | 配餐最后 |

同类型物品按距离中心远近排序，近的先抓。

## 放置区域默认配置

| 物品 | 放置位置（机械臂坐标） |
|------|------------------------|
| 可乐 | (100, 50, -31.2) |
| 汉堡 | (100, 0, -31.2) |
| 薯条 | (100, -50, -31.2) |

## 路径规划说明

1. **安全高度**：所有水平移动在 80mm 高度进行
2. **避障策略**：检测到障碍物时绕行
3. **运动顺序**：抬升 → 水平移动 → 下降

## 使用规则

1. 执行前先调用 `01_detect_and_sort.py` 确认物品数量
2. 可通过 `--place-zone` 自定义放置区域
3. 调试时使用 `--dry-run` 参数
4. 依赖 `vision-detect` 和 `coord-transform` skill
