---
name: furniture-organize
description: 家具整理：视觉识别桌面物品，按优先级分类抓取，路径规划避障，放置到指定区域。当用户提到整理桌子、收拾东西、分类物品、整理家具、夹取汉堡、夹取可乐、夹取薯条时使用。
allowed-tools: [exec]
---

# furniture-organize

桌面物品整理技能：自动识别、优先级排序、路径规划、避障抓取放置。

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
    {"class": "cola", "label": "可乐", "cx": 240.0, "cy": 185.0, "arm_x": 170.0, "arm_y": 70.0, "priority": 40.0, "rank": 1},
    {"class": "hanbao", "label": "汉堡", "cx": 320.0, "cy": 200.0, "arm_x": 163.0, "arm_y": 53.0, "priority": 30.0, "rank": 2},
    {"class": "shutiao", "label": "薯条", "cx": 180.0, "cy": 150.0, "arm_x": 130.0, "arm_y": 25.0, "priority": 10.0, "rank": 3}
  ],
  "count": 3,
  "status": "ok"
}
```

### 02_plan_path.py — 路径规划（备用模块）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/02_plan_path.py --start 150,0,80 --end 163,53,-31
```

参数：
- `--start x,y,z`：起点坐标（机械臂坐标，默认150,0,80）
- `--end x,y,z`：终点坐标（机械臂坐标）
- `--obstacles x1,y1,z1,r1;x2,y2,z2,r2`：障碍物列表（可选）

说明：此模块为备用模块，当前版本的避障逻辑已集成到 03_grab_and_place.py 中。

### 03_grab_and_place.py — 抓取放置执行（写操作，v3.0 重构版）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/03_grab_and_place.py --obj hanbao --grab-pos 163,53,-31 --place 100,0,-31
```

参数：
- `--obj class_name`：物品类别（cola/hanbao/shutiao/panzi）
- `--grab-pos x,y,z`：抓取位置坐标（机械臂坐标）
- `--place x,y,z`：放置位置坐标（机械臂坐标）
- `--obstacles x1,y1,z1,r1;x2,y2,z2,r2`：障碍物列表（可选，半径30mm）
- `--no-avoid`：关闭避障功能（更快）
- `--no-safe`：不经过安全位（直接路径）
- `--json`：JSON格式输出

输出示例：
```json
{
  "success": true,
  "object": "hanbao",
  "label": "汉堡",
  "grab_position": {"x": 163.0, "y": 53.0, "z": -31.0},
  "place_position": {"x": 100.0, "y": 0.0, "z": -31.0},
  "obstacles_count": 1,
  "avoid_enabled": true,
  "safe_enabled": true
}
```

### 04_run_organize.py — 批量整理主流程（写操作）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/04_run_organize.py
```

参数：
- `--dry-run`：只规划不执行（调试用）
- `--json`：JSON格式输出

用途：完整的整理流程：检测 → 排序 → 规划 → 抓取 → 放置（按优先级顺序）

输出示例：
```json
{
  "total_objects": 3,
  "success_count": 3,
  "fail_count": 0,
  "details": [
    {"object": "cola", "label": "可乐", "status": "ok"},
    {"object": "hanbao", "label": "汉堡", "status": "ok"},
    {"object": "shutiao", "label": "薯条", "status": "ok"}
  ],
  "status": "ok"
}
```

### 05_grab_avoid.py — 智能抓取（自动避障，v3.0 新增）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/furniture-organize/scripts/05_grab_avoid.py --target hanbao
```

参数：
- `--target class_name`：目标物品类别（cola/hanbao/shutiao/panzi）
- `--place x,y,z`：放置位置坐标（可选，默认使用放置区域）
- `--no-avoid`：关闭避障功能（更快）
- `--json`：JSON格式输出

用途：智能抓取单个物品，自动识别其他物品作为障碍物并避障

输出示例：
```json
{
  "target": "hanbao",
  "target_label": "汉堡",
  "grab_position": [163.0, 53.0, -31.2],
  "place_position": [86.7, -15.0, -31.2],
  "obstacles_count": 2,
  "avoid_enabled": true,
  "status": "ok"
}
```

## 优先级规则

| 优先级 | 物品 | 分数 | 说明 |
|--------|------|------|------|
| 1（最高） | 可乐 | 40 | 饮料先放，防止倾倒 |
| 2 | 汉堡 | 30 | 主食其次 |
| 3 | 盘子 | 20 | 餐具 |
| 4（最低） | 薯条 | 10 | 配餐最后 |

同类型物品按距离中心远近排序，近的先抓。

## 放置区域配置

放置区域：(90, 110) 到 (145, 170)

```
y=170 ┌─────┬─────┬─────┐
      │  0  │  1  │  2  │
y=140 ├─────┼─────┼─────┤
      │  3  │  4  │  5  │
y=110 └─────┴─────┴─────┘
      x=90  x=117 x=145
```

物品按优先级依次放在这些位置，避免重复放置：
- 第1个物品 → 位置0 (99.2, 125)
- 第2个物品 → 位置1 (117.5, 125)
- 第3个物品 → 位置2 (135.8, 125)
- 第4个物品 → 位置3 (99.2, 155)
- 第5个物品 → 位置4 (117.5, 155)
- 第6个物品 → 位置5 (135.8, 155)

**避免重复放置：** 已放置位置保存在 `placed_positions.json` 文件中，每次抓取前会加载，抓取后会更新。

## 避障配置

- **障碍物半径**：30mm
- **最小安全距离**：50mm
- **安全高度**：80mm

## 路径规划说明

1. **转向**：机械臂先转向目标方向（atan2计算）
2. **避障**：检测到障碍物时绕行（半径30mm）
3. **悬停**：移动到目标上方25mm悬停
4. **下降**：下降到目标位置
5. **安全位**：抓取/放置后经过安全位过渡

## 使用规则

1. **批量整理**：使用 `04_run_organize.py`，按优先级整理所有物品
2. **智能抓取**：使用 `05_grab_avoid.py --target xxx`，抓取指定物品并避障
3. **调试模式**：使用 `--dry-run` 参数只规划不执行
4. **依赖**：vision-detect（YOLO检测）、coord-transform（坐标转换）、arm-basic（机械臂控制）

## 飞书指令示例

| 用户指令 | 系统响应 |
|---------|---------|
| 整理桌子 | 调用 04_run_organize.py，批量整理所有物品 |
| 夹取汉堡 | 调用 05_grab_avoid.py --target hanbao |
| 夹取可乐 | 调用 05_grab_avoid.py --target cola |
| 夹取薯条 | 调用 05_grab_avoid.py --target shutiao |
| 看看桌上有什么 | 调用 01_detect_and_sort.py，只检测不抓取 |
