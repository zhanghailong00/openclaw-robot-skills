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

# 默认放置位置
DEFAULT_PLACE_ZONES = {
    'cola': {'x': 100, 'y': 50, 'z': -31.2},
    'hanbao': {'x': 100, 'y': 0, 'z': -31.2},
    'shutiao': {'x': 100, 'y': -50, 'z': -31.2},
    'panzi': {'x': 50, 'y': 0, 'z': -31.2},
}


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
                'radius': 30,  # 默认半径30mm
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
        place_zone = DEFAULT_PLACE_ZONES.get(args.target, DEFAULT_PLACE_ZONES['hanbao'])
        place_pos = [place_zone['x'], place_zone['y'], place_zone['z']]

    print(f"\n放置位置：({place_pos[0]}, {place_pos[1]}, {place_pos[2]})")

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
