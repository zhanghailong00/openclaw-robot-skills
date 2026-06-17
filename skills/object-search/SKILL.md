---
name: object-search
description: 物体搜寻：识别堆叠状态，推倒堆叠，检测散落物品，调用家居整理 skill 排列。当用户提到堆叠、推倒、搜寻物品、找东西时使用。
allowed-tools: [exec]
---

# object-search

物体搜寻技能：识别堆叠状态，推倒堆叠，检测散落物品，自动整理排列。

## 脚本目录

`/home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/`

## 脚本列表

### 完整流程脚本

#### 01_stack_and_arrange.py — 堆叠方块整理（写操作）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/01_stack_and_arrange.py
```

参数：无
用途：完整的堆叠方块整理流程：检测 → 推倒 → 检测 → 排列

### 分步调试脚本

#### 01_detect.py — 步骤1：检测桌面物品（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/01_detect.py
```

功能：调用 YOLO 检测桌面物品，输出检测结果
输出：物品数量、类别、像素坐标

#### 02_check_stack.py — 步骤2：判断是否需要推倒（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/02_check_stack.py
```

功能：检测桌面物品，判断是否堆叠，是否需要推倒
输出：是否堆叠、是否齐全、下一步动作

#### 03_calc_position.py — 步骤3：计算堆叠位置（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/03_calc_position.py
```

功能：检测桌面物品，计算堆叠位置（像素坐标和机械臂坐标）
输出：堆叠中心、推倒位置

#### 04_push_over.py — 步骤4：执行推倒动作（写操作）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/04_push_over.py
```

功能：检测堆叠位置，执行机械臂推倒动作
输出：推倒过程、推倒结果

#### 05_check_result.py — 步骤5：检测推倒后状态（只读）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/05_check_result.py
```

功能：推倒后检测桌面物品状态，判断是否需要继续推倒
输出：物品数量、类别、是否齐全

#### 06_arrange.py — 步骤6：使用家居整理排列（写操作）

```bash
/usr/local/miniconda3/bin/python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/06_arrange.py
```

功能：调用家居整理 skill 排列物品
输出：抓取过程、排列结果

## 工作流程

```
1. 检测桌面物品（YOLO）
   ↓
2. 判断是否检测到所有目标物品（可乐、薯条、汉堡）
   ↓
   ├─ 是 → 进入步骤5
   ↓
   └─ 否 → 继续推倒
   ↓
3. 计算堆叠位置
   ↓
4. 机械臂推倒堆叠
   ↓
   回到步骤1（最多5次）
   ↓
5. 使用家居整理 skill 排列
   ↓
6. 完成
```

## 配置参数

```python
# 推倒配置
MAX_PUSH_COUNT = 5      # 最大推倒次数

# 推倒参数
above_height = 100      # 物体上方高度（mm）
left_distance = 20      # 向左移动距离（mm）
down_height = 70        # 下降高度（mm）
right_distance = 80     # 向右推倒距离（mm）

# 目标物品（只有可乐、汉堡、薯条，盘子无法堆叠）
TARGET_ITEMS = {'cola', 'hanbao', 'shutiao'}

# 安全位置（离开工作区，不遮挡摄像头）
SAFE_HEIGHT = 30        # 安全高度（mm）
SAFE_POS = [20, -130, 30] # 安全位坐标
```

## 推倒方式

**上方左移下降右移推倒：**
1. 移动到物体上方100mm
2. 水平向左移动20mm（Y轴负方向）
3. 下降高度70mm
4. 向右移动80mm（推倒，Y轴正方向）
5. 抬起到安全高度

**推倒参数：**
- 物体上方高度：100mm
- 向左移动距离：20mm
- 下降高度：70mm
- 向右推倒距离：80mm

**优势：**
- 更精准，从上方接近
- 推倒幅度可控（80mm）
- 不会把物品推飞到远处

## 依赖的 Skill

| Skill | 用途 |
|-------|------|
| vision-detect | YOLO 物品检测 |
| coord-transform | 像素坐标转机械臂坐标 |
| furniture-organize | 家居整理（抓取排列） |

## 使用场景

### 场景1：堆叠方块整理

**初始状态：**
```
┌─────┐
│ 🍔 │  ← 顶层：汉堡
├─────┤
│ 🍟 │  ← 中层：薯条
├─────┤
│ 🥤 │  ← 底层：可乐
└─────┘
```

**目标状态：**
```
┌─────┐  ┌─────┐  ┌─────┐
│ 🍔 │  │ 🍟 │  │ 🥤 │
└─────┘  └─────┘  └─────┘
汉堡区    薯条区    可乐区
```

### 场景2：散落物品搜寻

**初始状态：** 物品散落在桌面各处

**目标状态：** 物品整齐排列在指定区域

## 飞书指令示例

| 用户指令 | 系统响应 |
|---------|---------|
| 整理堆叠 | 调用 01_stack_and_arrange.py |
| 推倒堆叠 | 调用 01_stack_and_arrange.py |
| 搜寻物品 | 调用 01_stack_and_arrange.py |
| 找东西 | 调用 01_stack_and_arrange.py |

## 注意事项

1. **最大推倒次数**：默认5次，避免无限循环
2. **推倒参数**：上方100mm，左移20mm，下降70mm，右移80mm
3. **等待时间**：推倒后等待1.5秒，让方块稳定
4. **目标物品**：可乐、薯条、汉堡，可修改配置
5. **已放置位置**：保存在 `placed_positions.json` 文件中，避免重复放置

## 测试方法

### 测试1：堆叠方块整理

```bash
# 1. 把3个方块摞在一起
# 2. 运行脚本
python /home/HwHiAiUser/.openclaw/workspace/skills/object-search/scripts/01_stack_and_arrange.py
```

### 测试2：观察推倒过程

```bash
# 观察机械臂推倒动作
# 观察方块散落情况
# 观察家居整理过程
```

## 扩展功能

### 1. 自定义目标物品

修改脚本中的 `TARGET_ITEMS` 配置：

```python
TARGET_ITEMS = {'cola', 'hanbao', 'shutiao', 'panzi'}  # 添加盘子
```

### 2. 自定义推倒方向

修改推倒方向逻辑：

```python
# 固定方向
direction = 'right'

# 或根据堆叠位置动态选择
if stack_pos[1] > 0:
    direction = 'left'
else:
    direction = 'right'
```

### 3. 添加语音交互

在飞书中说"整理堆叠"，自动触发脚本。

---

> 版本：v1.0
> 创建日期：2026-06-16
> 依赖：furniture-organize, vision-detect, coord-transform
