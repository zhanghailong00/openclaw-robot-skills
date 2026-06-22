#!/usr/local/miniconda3/bin/python
"""
家具整理 - 智能抓取（自动避障）

功能：
1. 检测桌面上所有物品
2. 用户指定要抓取的目标物品
3. 其他物品自动作为障碍物
4. 规划路径避开障碍物，抓取目标

用法：
  python 05_grab_avoid.py --target shutiao
  python 05_grab_avoid.py --target cola --place 100,50,-31
  python 05_grab_avoid.py --target hanbao --no-avoid  # 关闭避障（更快）
"""

import sys
import os
import json
import math
import argparse
import subprocess

# ==================== 配置 ====================

PYTHON_PATH = "/usr/local/miniconda3/bin/python"
SKILLS_DIR = "/home/HwHiAiUser/.openclaw/workspace/skills"

# 脚本路径
DETECT_SCRIPT = os.path.join(SKILLS_DIR, "vision-detect/scripts/02_run_detection.py")
COORD_SCRIPT = os.path.join(SKILLS_DIR, "coord-transform/scripts/02_convert.py")
GRAB_PLACE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_grab_and_place.py")

# 安全高度
SAFE_HEIGHT = 80

# 物品中文名称
TYPE_LABELS = {
    'cola': '可乐',
    'hanbao': '汉堡',
    'shutiao': '薯条',
    'panzi': '盘子',
}

# 放置区域配置（根据实测物品位置）
PLACE_AREA = {
    'x_min': 78,    # X左边界
    'x_max': 183,   # X右边界
    'y_min': 10,    # Y下边界
    'y_max': 96,    # Y上边界
    'z': -31.2      # 放置高度
}

# 网格排列配置
GRID_COLS = 2  # 每行2个（增大间距）
GRID_ROWS = 3  # 最多3行

# 已放置位置记录文件路径（放在 skill 目录下）
PLACED_POSITIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placed_positions.json")

# 已放置位置记录（避免重复放置）
placed_positions = []


def load_placed_positions():
    """从文件加载已放置位置"""
    global placed_positions
    try:
        if os.path.exists(PLACED_POSITIONS_FILE):
            with open(PLACED_POSITIONS_FILE, 'r') as f:
                placed_positions = json.load(f)
    except:
        placed_positions = []


def save_placed_positions():
    """保存已放置位置到文件"""
    try:
        with open(PLACED_POSITIONS_FILE, 'w') as f:
            json.dump(placed_positions, f)
    except:
        pass


def get_place_position(index):
    """
    根据索引计算放置位置（均匀分布在区域内，避免重复）

    参数：
        index: 物品索引（0, 1, 2, ...）

    返回：
        [x, y, z] 放置位置
    """
    global placed_positions

    # 如果 placed_positions 为空，尝试从文件加载
    if not placed_positions:
        load_placed_positions()

    # 计算所有可能的位置
    all_positions = []
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = PLACE_AREA['x_min'] + (PLACE_AREA['x_max'] - PLACE_AREA['x_min']) * (col + 0.5) / GRID_COLS
            y = PLACE_AREA['y_min'] + (PLACE_AREA['y_max'] - PLACE_AREA['y_min']) * (row + 0.5) / GRID_ROWS
            z = PLACE_AREA['z']
            all_positions.append([x, y, z])

    # 过滤掉已放置的位置
    available_positions = []
    for pos in all_positions:
        is_used = False
        for placed in placed_positions:
            # 如果位置距离小于30mm，认为是相同位置
            distance = math.sqrt((pos[0]-placed[0])**2 + (pos[1]-placed[1])**2)
            if distance < 30:
                is_used = True
                break
        if not is_used:
            available_positions.append(pos)

    # 如果有可用位置，返回第一个
    if available_positions:
        selected_pos = available_positions[0]
        placed_positions.append(selected_pos)
        # 保存到文件
        save_placed_positions()
        return selected_pos

    # 如果没有可用位置，返回默认位置（强制放置）
    default_pos = all_positions[index % len(all_positions)]
    placed_positions.append(default_pos)
    # 保存到文件
    save_placed_positions()
    return default_pos


def reset_placed_positions():
    """重置已放置位置记录"""
    global placed_positions
    placed_positions = []


# ==================== 工具函数 ====================

def run_script(script_path, args=None):
    """运行子脚本并解析JSON"""
    cmd = [PYTHON_PATH, script_path]
    if args:
        cmd.extend(args)

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 解析JSON（处理多行输出）
    stdout = result.stdout.strip()
    json_objects = []
    i = 0
    while i < len(stdout):
        start = stdout.find('{', i)
        if start == -1:
            break

        depth = 0
        end = start
        for j in range(start, len(stdout)):
            if stdout[j] == '{':
                depth += 1
            elif stdout[j] == '}':
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break

        if depth == 0:
            json_str = stdout[start:end]
            try:
                obj = json.loads(json_str)
                json_objects.append(obj)
            except json.JSONDecodeError:
                pass
            i = end
        else:
            i = start + 1

    return json_objects[-1] if json_objects else None


def detect_objects():
    """检测桌面上所有物品"""
    print("正在检测桌面物品...")
    result = run_script(DETECT_SCRIPT)

    if not result or result.get('status') != 'ok':
        return []

    detections = result.get('detections', [])

    # 坐标转换
    objects = []
    for det in detections:
        coord_result = run_script(COORD_SCRIPT, ["--px", str(det['cx']), "--py", str(det['cy']), "--json"])

        if coord_result and 'arm_target' in coord_result:
            arm = coord_result['arm_target']
            obj = {
                'class': det['class'],
                'label': det['label'],
                'confidence': det['confidence'],
                'cx': det['cx'],
                'cy': det['cy'],
                'arm_x': arm['x'],
                'arm_y': arm['y'],
                'arm_z': arm['z'],
            }
            objects.append(obj)

    return objects


# ==================== 主函数 ====================

def main():
    """主函数"""
    # 加载已放置位置记录
    load_placed_positions()

    parser = argparse.ArgumentParser(description='家具整理 - 智能抓取（自动避障）')
    parser.add_argument('--target', type=str, required=True,
                        help='目标物品类别（cola/hanbao/shutiao/panzi）')
    parser.add_argument('--place', type=str, default='',
                        help='放置位置 x,y,z（可选，默认使用预设位置）')
    parser.add_argument('--no-avoid', action='store_true',
                        help='关闭避障功能（更快）')
    parser.add_argument('--json', action='store_true',
                        help='JSON格式输出')

    args = parser.parse_args()

    # 1. 检测所有物品
    print("=" * 50)
    print("智能抓取（自动避障）")
    print("=" * 50)

    objects = detect_objects()

    if not objects:
        print("未检测到任何物品")
        return

    print(f"\n检测到 {len(objects)} 个物品：")
    for i, obj in enumerate(objects):
        print(f"  {i+1}. {obj['label']} ({obj['class']}) - 位置: ({obj['arm_x']:.1f}, {obj['arm_y']:.1f})")

    # 2. 分离目标和障碍物
    target_obj = None
    obstacles = []

    for obj in objects:
        if obj['class'] == args.target:
            target_obj = obj
        else:
            # 其他物品作为障碍物
            obstacles.append({
                'center': [obj['arm_x'], obj['arm_y'], SAFE_HEIGHT],
                'radius': 30,  # 障碍物半径30mm
                'label': obj['label']
            })

    if not target_obj:
        print(f"\n错误：未找到目标物品 '{args.target}'")
        print(f"可用物品：{[obj['class'] for obj in objects]}")
        return

    print(f"\n目标物品：{target_obj['label']} ({target_obj['class']})")
    print(f"抓取位置：({target_obj['arm_x']:.1f}, {target_obj['arm_y']:.1f}, -31.2)")

    if obstacles:
        print(f"\n障碍物（{len(obstacles)}个）：")
        for obs in obstacles:
            print(f"  - {obs['label']}: ({obs['center'][0]:.1f}, {obs['center'][1]:.1f})")

    # 3. 确定放置位置
    if args.place:
        place_pos = [float(x) for x in args.place.split(',')]
    else:
        # 使用放置区域，均匀分布
        place_pos = get_place_position(0)  # 第一个物品
        print(f"\n放置区域：({PLACE_AREA['x_min']},{PLACE_AREA['y_min']}) 到 ({PLACE_AREA['x_max']},{PLACE_AREA['y_max']})")

    print(f"\n放置位置：({place_pos[0]:.1f}, {place_pos[1]:.1f}, {place_pos[2]})")

    # 4. 构建障碍物参数
    obstacles_str = ";".join([
        f"{obs['center'][0]},{obs['center'][1]},{obs['center'][2]},{obs['radius']}"
        for obs in obstacles
    ])

    # 5. 执行抓取
    print("\n开始抓取...")
    grab_pos = [target_obj['arm_x'], target_obj['arm_y'], -31.2]

    cmd = [
        PYTHON_PATH,
        GRAB_PLACE_SCRIPT,
        "--obj", args.target,
        "--grab-pos", ",".join([str(x) for x in grab_pos]),
        "--place", ",".join([str(x) for x in place_pos]),
    ]

    if obstacles_str:
        cmd.extend(["--obstacles", obstacles_str])

    if args.no_avoid:
        cmd.append("--no-avoid")

    result = subprocess.run(cmd, capture_output=False, text=True)

    # 保存已放置位置到文件
    save_placed_positions()

    # 输出结果
    if args.json:
        output = {
            "target": args.target,
            "target_label": target_obj['label'],
            "grab_position": grab_pos,
            "place_position": place_pos,
            "obstacles_count": len(obstacles),
            "avoid_enabled": not args.no_avoid,
            "status": "ok"
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
